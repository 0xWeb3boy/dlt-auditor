---
case_id: case_20170825_08f27428b
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2017-08-25
source_refs:
  - git:08f27428b4e97c339a220b7155ad13f4ef5a6767
  - "core/vm/evm.go:312"
  - "core/vm/errors.go:20"
  - "core/vm/evm.go:26"
bug_class: contract-address-collision
impact_type:
  - state-integrity
confidence: medium
tags:
  - evm
  - contract-creation
  - address-collision
  - protocol-invariant
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch implements Metropolis EIP 684 behavior in go-ethereum's EVM CREATE path by rejecting contract creation when the computed destination address already appears occupied. The evidence supports a protocol-semantics/state-integrity change, but it does not establish an exploitable vulnerability or a concrete security fix in released deployments.

## Observed Patch Facts

1. In `core/vm/evm.go`, the patch replaces `// Create a new account on the state` with `// Ensure there's no existing contract already at the designated address`.

2. In `core/vm/errors.go`, the patch replaces `ErrOutOfGas = errors.New("out of gas")` with `ErrOutOfGas = errors.New("out of gas")`.

3. In `core/vm/evm.go`, the patch adds `// emptyCodeHash is used by create to ensure deployment is disallowed to already`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `storage` area of the project. Historical context from `core/vm/contracts.go`, `core/vm/instructions.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/instructions.go`, `core/vm/noop.go`. The strongest project-level identifiers around this patch are `errors`, `StateDB`, `contract`, and `common`. Nearby tests or test-like files include `core/vm/runtime/fuzz.go`.

## Before/After Behavior

Before the patch, the supplied EVM.Create snippet shows nonce handling and continuation toward account creation without a visible check that the computed CREATE address was unoccupied. After the patch, EVM.Create computes the destination address, checks the destination nonce and code hash, and returns ErrContractAddressCollision when the address is occupied.

# Root Cause

The provided evidence supports a missing pre-creation occupancy check in the EVM CREATE path relative to the Metropolis EIP 684 rule. It does not prove that this omission was exploitable as a vulnerability.

## Walkthrough

1. EVM.Create performs the existing recursion, depth, and balance checks.

2. The function reads the caller nonce, increments it, and derives the prospective contract address with crypto.CreateAddress.

3. The patched code reads StateDB.GetCodeHash for the computed destination and checks StateDB.GetNonce for that same address.

4. If the destination has a nonzero nonce, creation fails with ErrContractAddressCollision.

5. If the destination has a code hash other than the zero hash or emptyCodeHash, creation also fails with ErrContractAddressCollision.

6. Only non-colliding creation proceeds toward the existing snapshot/account-creation flow.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/evm.go | 301 | EVM Create path computes the contract address and rejects creation when the destination account already has nonce or code. |
| core/vm/evm.go | 26 | Defines emptyCodeHash used to distinguish genuinely empty code from deployed/non-empty code during collision checks. |
| core/vm/errors.go | 20 | Adds ErrContractAddressCollision as the failure mode for rejected contract creation collisions. |

## Code Snippets

## Snippet 1

Context: `core/vm/evm.go:312` (changes signature or replay validation logic)

Before
```go
return nil, common.Address{}, gas, ErrInsufficientBalance
	}

	// Create a new account on the state
	nonce := evm.StateDB.GetNonce(caller.Address())
	evm.StateDB.SetNonce(caller.Address(), nonce+1)

	snapshot := evm.StateDB.Snapshot()
```
After
```go
return nil, common.Address{}, gas, ErrInsufficientBalance
	}
	// Ensure there's no existing contract already at the designated address
	nonce := evm.StateDB.GetNonce(caller.Address())
	evm.StateDB.SetNonce(caller.Address(), nonce+1)

	contractAddr = crypto.CreateAddress(caller.Address(), nonce)
	contractHash := evm.StateDB.GetCodeHash(contractAddr)
```

## Snippet 2

Context: `core/vm/errors.go:20` (changes bounds, limits, or capacity handling)

Before
```go
var (
	ErrOutOfGas            = errors.New("out of gas")
	ErrCodeStoreOutOfGas   = errors.New("contract creation code storage out of gas")
	ErrDepth               = errors.New("max call depth exceeded")
	ErrTraceLimitReached   = errors.New("the number of logs reached the specified limit")
	ErrInsufficientBalance = errors.New("insufficient balance for transfer")
)
```
After
```go
var (
	ErrOutOfGas                 = errors.New("out of gas")
	ErrCodeStoreOutOfGas        = errors.New("contract creation code storage out of gas")
	ErrDepth                    = errors.New("max call depth exceeded")
	ErrTraceLimitReached        = errors.New("the number of logs reached the specified limit")
	ErrInsufficientBalance      = errors.New("insufficient balance for transfer")
	ErrContractAddressCollision = errors.New("contract address collision")
```

## Snippet 3

Context: `core/vm/evm.go:26` (changes a sensitive control or state-update path)

Before
```go
)

type (
	CanTransferFunc func(StateDB, common.Address, *big.Int) bool
```
After
```go
)

// emptyCodeHash is used by create to ensure deployment is disallowed to already
// deployed contract addresses (relevant after the account abstraction).
var emptyCodeHash = crypto.Keccak256Hash(nil)

type (
	CanTransferFunc func(StateDB, common.Address, *big.Int) bool
```

# Fix Pattern

Add a fail-closed protocol invariant check at the contract-creation boundary before downstream account creation proceeds.

## How It Was Fixed

The patch adds emptyCodeHash, checks the computed contract address for a nonzero nonce or existing non-empty code hash, and introduces ErrContractAddressCollision as the explicit failure mode.

# Why It Matters

1. Keeps CREATE behavior aligned with the Metropolis EIP 684 collision rule.

2. Prevents contract creation from proceeding at an already occupied computed address.

3. Makes the collision case explicit for callers and tests.

4. The supplied evidence does not show unauthorized fund transfer, storage overwrite, consensus split, or another concrete exploit path.

# Evidence Notes

Grounded evidence comes from core/vm/evm.go, where the CREATE path now checks StateDB.GetNonce and StateDB.GetCodeHash for the computed address, and core/vm/errors.go, where ErrContractAddressCollision is added. The commit subject identifies this as implementing Metropolis EIP 684. Test files are listed, but no test hunks are provided, so specific regression behavior should not be inferred. Protocol security invariant: EVM contract creation should fail when the deterministic CREATE destination is already occupied, evidenced here by a nonzero nonce or a non-empty deployed code hash. Verification notes: Patch evidence does not prove an exploitable vulnerability in released deployments. Patch evidence does not show unauthorized fund transfer or direct storage overwrite by itself. Patch evidence does not establish a remote attack path beyond invalid contract creation semantics. This appears to implement a protocol rule, not merely fix an ordinary implementation crash or memory-safety bug. Downgraded from likely security-hardening to unclear because exploitability is not established by the supplied evidence. Kept the subsystem and collision-handling description because they are directly supported by the changed EVM.Create code. Removed claims of state corruption, fund impact, storage overwrite, or demonstrated attack path. Excluded from the security corpus because the evidence supports protocol implementation more than a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `contract-address-collision`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `evm, contract-creation, address-collision, protocol-invariant, state-integrity`

The patch adds an explicit fail-closed check in the EVM CREATE path to reject contract creation when the deterministic destination address already has a nonce or non-empty code hash. The evidence does not prove a concrete exploitable vulnerability or released security incident, but it clearly tightens a security-sensitive protocol/state invariant around contract address collision, so it is best retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. EVM.Create now computes the destination address before account creation and checks StateDB.GetNonce for occupancy.
2. EVM.Create now checks StateDB.GetCodeHash and rejects addresses with existing non-empty code.
3. A new ErrContractAddressCollision failure mode makes collision rejection explicit.
4. The commit subject states this implements Metropolis EIP 684, a protocol rule governing contract creation collisions.

## Missing Evidence

1. No exploit scenario is shown in the supplied patch evidence.
2. No evidence shows unauthorized fund transfer, storage overwrite, consensus split, or remote attack path.
3. No test hunks are provided to demonstrate the exact regression case.
4. No advisory, CVE, or security note is included in the commit metadata.

## Claim Boundaries

1. Treat as protocol security hardening, not a proven vulnerability fix.
2. Do not claim demonstrated state corruption or storage overwrite from the supplied evidence alone.
3. Do not claim concrete exploitability in released deployments.
4. The supported behavior change is limited to rejecting CREATE when the computed address is already occupied.
