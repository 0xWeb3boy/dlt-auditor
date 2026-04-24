---
case_id: case_20170825_08f27428b4
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
bug_class: contract-address-collision-prevention
impact_type:
  - state-integrity
  - consensus-integrity
confidence: medium
tags:
  - evm
  - contract-creation
  - address-collision
  - protocol-rule
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch implements the Metropolis/EIP-684 contract address collision rule in go-ethereum's EVM CREATE path. It adds a guard that computes the destination address, checks the target account nonce and code hash, and returns a new collision error if the address is already occupied. The evidence supports protocol-rule enforcement, but it does not establish an exploitable vulnerability or concrete security failure.

## Observed Patch Facts

1. In `core/vm/evm.go`, the patch replaces `// Create a new account on the state` with `// Ensure there's no existing contract already at the designated address`.

2. In `core/vm/errors.go`, the patch replaces `ErrOutOfGas = errors.New("out of gas")` with `ErrOutOfGas = errors.New("out of gas")`.

3. In `core/vm/evm.go`, the patch adds `// emptyCodeHash is used by create to ensure deployment is disallowed to already`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `storage` area of the project. Historical context from `core/vm/contracts.go`, `core/vm/instructions.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/instructions.go`, `core/vm/noop.go`. The strongest project-level identifiers around this patch are `errors`, `StateDB`, `contract`, and `common`. Nearby tests or test-like files include `core/vm/runtime/fuzz.go`.

## Before/After Behavior

Before the patch, the provided `EVM.Create` snippet shows balance checking, caller nonce reading/incrementing, and then proceeding toward account creation without a visible guard for an already-occupied derived contract address. After the patch, `EVM.Create` computes `contractAddr`, reads the target code hash, and rejects creation if the target account has a nonzero nonce or a code hash indicating non-empty code. The patch also adds `emptyCodeHash` and `ErrContractAddressCollision`.

# Root Cause

The prior CREATE path shown in the evidence did not visibly enforce the EIP-684 collision condition before account creation proceeded. The evidence does not show that this omission caused an exploitable vulnerability.

## Walkthrough

1. `core/vm/evm.go` adds `emptyCodeHash = crypto.Keccak256Hash(nil)` for distinguishing empty-code account state.

2. `EVM.Create` still performs recursion depth and balance checks first.

3. The patched path reads and increments the caller nonce, then computes the CREATE-derived contract address.

4. The code reads the target account code hash from `StateDB`.

5. The new guard rejects creation if the target account nonce is nonzero or if the target has non-empty code.

6. On rejection, `EVM.Create` returns `ErrContractAddressCollision`.

7. `core/vm/errors.go` adds the explicit `ErrContractAddressCollision` error value.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/evm.go | 26 | defines emptyCodeHash used to distinguish empty-code accounts from deployed-code accounts during collision checks |
| core/vm/evm.go | 312 | EVM Create path computes the contract address and rejects nonzero nonce or non-empty code hash before account creation |
| core/vm/errors.go | 20 | adds explicit ErrContractAddressCollision returned by the CREATE collision guard |

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

Add a pre-creation protocol-rule check at the EVM CREATE state-transition boundary and fail fast when the derived destination address is already occupied.

## How It Was Fixed

The fix moves contract-address derivation before account creation, checks the destination account's nonce and code hash through `StateDB`, permits zero hash and `emptyCodeHash` as empty-code cases, and returns `ErrContractAddressCollision` for collisions. The commit metadata also indicates related tests were updated, but the supplied evidence does not include test bodies.

# Why It Matters

1. Enforces the Metropolis/EIP-684 CREATE collision rule.

2. Prevents creation from continuing when the derived address is already occupied under the shown condition.

3. Touches a consensus-sensitive EVM state-transition path.

4. Does not, by itself, prove a vulnerability or exploit path.

# Evidence Notes

The strongest evidence is the `EVM.Create` hunk adding `StateDB.GetNonce`, `StateDB.GetCodeHash`, and `ErrContractAddressCollision` handling for the derived `contractAddr`. Supporting evidence is the new error in `core/vm/errors.go` and the `emptyCodeHash` helper in `core/vm/evm.go`. The supplied evidence does not prove remote exploitability, arbitrary overwrite, chain split, or a concrete consensus failure scenario. Protocol security invariant: Contract creation should fail when the CREATE-derived destination address already has a nonzero nonce or non-empty code under the Metropolis/EIP-684 rule. Verification notes: Does not prove remote exploitability from the patch alone Does not show a concrete chain split or consensus failure scenario in the provided evidence Does not prove arbitrary state overwrite; it only shows missing enforcement of the EIP-684 collision rule Does not establish this as a vulnerability fix rather than Metropolis protocol-rule implementation No command execution or external context was used. Classification is limited to the supplied snippets and metadata. Security relevance is plausible because the path is consensus-sensitive, but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `contract-address-collision-prevention`
Final impact type: `state-integrity, consensus-integrity`
Final confidence: `medium`
Final tags: `evm, contract-creation, address-collision, protocol-rule, state-integrity`

The supplied patch evidence clearly adds a new EVM CREATE guard that prevents contract creation at an already-occupied derived address by checking target nonce and code hash and returning a dedicated collision error. This is best treated as security hardening of a consensus-sensitive state transition, not a proven security fix, because the evidence frames it as Metropolis/EIP-684 implementation and does not show an exploit, incident, or concrete vulnerability outcome.

## Security Evidence

1. EVM.Create now computes the derived contract address before account creation and checks existing state for that address.
2. Creation is rejected when the destination account has a nonzero nonce or non-empty code hash.
3. A dedicated ErrContractAddressCollision error was added for this failure condition.
4. The helper emptyCodeHash is explicitly documented as supporting disallowing deployment to already deployed contract addresses.

## Missing Evidence

1. No exploit path or attacker-controlled overwrite scenario is shown.
2. No test body demonstrates a security regression or malicious case.
3. No advisory, CVE, incident, or vulnerability language is provided.
4. The commit subject indicates protocol implementation rather than an explicit bug or security fix.

## Claim Boundaries

1. Do not claim arbitrary state overwrite is proven by the supplied evidence.
2. Do not claim remote exploitability or chain split is demonstrated.
3. Do not classify as a confirmed security-fix; the supported classification is protocol security hardening.
4. The validated claim is limited to enforcing contract address collision prevention in the EVM CREATE path.
