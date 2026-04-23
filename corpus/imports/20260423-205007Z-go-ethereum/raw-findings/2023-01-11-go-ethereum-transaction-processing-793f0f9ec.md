---
case_id: case_20230111_793f0f9ec
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-01-11
source_refs:
  - git:793f0f9ec860f6f51e0cec943a268c10863097c7
  - "core/state_transition.go:338"
  - "core/state_transition.go:149"
  - "core/vm/gas_table.go:303"
  - "core/state_transition.go:170"
bug_class: resource-accounting-hardening
impact_type:
  - resource-exhaustion-mitigation
confidence: medium
tags:
  - go-ethereum
  - evm
  - transaction-processing
  - initcode
  - gas-metering
  - resource-limits
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch implements EIP-3860 initcode limits and metering for the Shanghai fork. The evidence supports protocol resource-accounting hardening, but it does not establish a pre-existing vulnerability, exploit path, malformed-input panic, remote DoS, or consensus failure.

## Observed Patch Facts

1. In `core/state_transition.go`, the patch replaces `// - prepare accessList(post-berlin)` with `// Check whether the init code size has been exceeded.`.

2. In `core/state_transition.go`, the patch replaces `z := uint64(len(data)) - nz` with `z := dataLen - nz`.

3. In `core/vm/gas_table.go`, the patch replaces `func gasExpFrontier(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi...` with `func gasCreateEip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memory...`.

4. In `core/state_transition.go`, the patch replaces `// NewStateTransition initialises and returns a new state transition object.` with `// toWordSize returns the ceiled word size required for init code payment calculation.`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/vm/interface.go`, `core/vm/instructions_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/interface.go`, `core/vm/instructions_test.go`. The strongest project-level identifiers around this patch are `size`, `params`, `uint64`, and `math`.

## Before/After Behavior

Before the patch, the supplied evidence does not show Shanghai-gated initcode size rejection or EIP-3860 per-word initcode gas in the shown contract-creation paths. After the patch, transaction validation rejects oversized Shanghai contract-creation initcode, intrinsic gas includes the EIP-3860 word charge, and VM CREATE-related gas calculation validates and meters stack-derived initcode size with overflow checks.

# Root Cause

No proven vulnerability root cause is established. The grounded issue is that the pre-change code did not yet implement the new Shanghai/EIP-3860 initcode resource-accounting rules across the shown transaction and EVM gas paths.

## Walkthrough

1. TransitionDb derives fork rules and whether the message is contract creation.

2. IntrinsicGas is called with rules.IsShanghai so fork activation can affect intrinsic gas.

3. IntrinsicGas adds params.InitCodeWordGas per ceil-word of initcode only for contract creation when EIP-3860 is active.

4. TransitionDb rejects Shanghai contract-creation transactions when len(st.data) exceeds params.MaxInitCodeSize.

5. toWordSize computes ceil(size/32) with a uint64 boundary guard for gas calculation.

6. gasCreateEip3860 validates stack-derived initcode size, rejects overflow or sizes above params.MaxInitCodeSize, adds initcode word gas, and uses checked addition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 338 | Rejects Shanghai contract-creation transactions whose initcode exceeds params.MaxInitCodeSize. |
| core/state_transition.go | 149 | Adds EIP-3860 per-word initcode cost to transaction intrinsic gas for contract creation. |
| core/vm/gas_table.go | 303 | Adds CREATE/CREATE2 initcode-size metering and overflow checks in EVM gas calculation. |
| core/state_transition.go | 170 | Computes ceil word size for initcode gas charging with uint64 overflow handling. |

## Code Snippets

## Snippet 1

Context: `core/state_transition.go:338` (changes bounds, limits, or capacity handling)

Before
```go
}

	// Execute the preparatory steps for state transition which includes:
	// - prepare accessList(post-berlin)
```
After
```go
}

	// Check whether the init code size has been exceeded.
	if rules.IsShanghai && contractCreation && len(st.data) > params.MaxInitCodeSize {
		return nil, fmt.Errorf("%w: code size %v limit %v", ErrMaxInitCodeSizeExceeded, len(st.data), params.MaxInitCodeSize)
	}

	// Execute the preparatory steps for state transition which includes:
```

## Snippet 2

Context: `core/state_transition.go:149` (changes a sensitive control or state-update path)

Before
```go
gas += nz * nonZeroGas

		z := uint64(len(data)) - nz
		if (math.MaxUint64-gas)/params.TxDataZeroGas < z {
			return 0, ErrGasUintOverflow
		}
		gas += z * params.TxDataZeroGas
	}
```
After
```go
gas += nz * nonZeroGas

		z := dataLen - nz
		if (math.MaxUint64-gas)/params.TxDataZeroGas < z {
			return 0, ErrGasUintOverflow
		}
		gas += z * params.TxDataZeroGas
```

## Snippet 3

Context: `core/vm/gas_table.go:303` (changes a sensitive control or state-update path)

Before
```go
}

func gasExpFrontier(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize uint64) (uint64, error) {
	expByteLen := uint64((stack.data[stack.len()-2].BitLen() + 7) / 8)
```
After
```go
}

func gasCreateEip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySize uint64) (uint64, error) {
	gas, err := memoryGasCost(mem, memorySize)
	if err != nil {
		return 0, err
	}
	size, overflow := stack.Back(2).Uint64WithOverflow()
```

## Snippet 4

Context: `core/state_transition.go:170` (changes a sensitive control or state-update path)

Before
```go
}

// NewStateTransition initialises and returns a new state transition object.
func NewStateTransition(evm *vm.EVM, msg Message, gp *GasPool) *StateTransition {
```
After
```go
}

// toWordSize returns the ceiled word size required for init code payment calculation.
func toWordSize(size uint64) uint64 {
	if size > math.MaxUint64-31 {
		return math.MaxUint64/32 + 1
	}
```

# Fix Pattern

Implement fork-gated resource accounting at relevant transaction and VM gas boundaries, with explicit size limits and checked uint64 gas arithmetic.

## How It Was Fixed

The patch added Shanghai-gated initcode size validation in core/state_transition.go, added EIP-3860 initcode word gas to IntrinsicGas, introduced a checked toWordSize helper, and added gasCreateEip3860 in core/vm/gas_table.go for CREATE-related initcode metering and overflow handling.

# Why It Matters

1. Aligns contract creation with Shanghai/EIP-3860 rules.

2. Bounds initcode size after the fork activates.

3. Charges initcode length as an explicit resource cost.

4. Reduces risk of unmetered or oversized initcode processing under the new protocol rules.

5. Does not prove a concrete exploitable pre-patch vulnerability from the supplied evidence.

# Evidence Notes

Primary evidence is from core/state_transition.go and core/vm/gas_table.go. The heuristic baseline's malformed-decoding and panic narrative is unsupported and should be discarded. The mapper's claim boundaries are appropriate: the evidence shows EIP-3860 implementation, not a demonstrated vulnerability fix. Protocol security invariant: After Shanghai, contract-creation initcode is bounded by params.MaxInitCodeSize and charged additional per-word initcode gas under EIP-3860. Verification notes: The patch does not prove a pre-existing remotely exploitable vulnerability in go-ethereum. The patch does not show malformed transaction decoding reaching a panic-prone conversion path. The patch does not establish chain split or consensus failure in pre-Shanghai rules; it implements new Shanghai fork behavior. The patch does not prove DoS exploitability beyond addressing protocol-level initcode resource accounting. No evidence proves remote exploitability. No evidence proves a pre-existing panic path. No evidence proves a chain split or consensus bug before Shanghai. Classified as security-relevant hardening, but not kept as a vulnerability-fix corpus item. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting-hardening`
Final impact type: `resource-exhaustion-mitigation`
Final confidence: `medium`
Final tags: `go-ethereum, evm, transaction-processing, initcode, gas-metering, resource-limits, protocol-hardening`

The supplied patch evidence supports security-relevant hardening rather than a concrete vulnerability fix. It implements Shanghai/EIP-3860 fork-gated initcode size limits, per-word gas metering, and checked arithmetic in transaction and VM gas paths. This clearly tightens resource-control behavior in a consensus-critical subsystem, but the evidence does not prove an exploitable pre-existing bug, remote DoS, panic, or consensus failure.

## Security Evidence

1. Adds Shanghai-gated rejection of contract-creation initcode larger than params.MaxInitCodeSize.
2. Adds EIP-3860 per-word initcode gas charging to IntrinsicGas for contract creation.
3. Adds CREATE-related initcode size validation and gas metering in core/vm/gas_table.go.
4. Uses overflow-aware calculations for gas accounting and word-size computation.

## Missing Evidence

1. No demonstrated exploit path or attacker-controlled transaction causing node failure is shown.
2. No evidence of a pre-patch consensus split or chain safety failure is provided.
3. No proof that the previous behavior violated then-active protocol rules before Shanghai activation.
4. No regression test evidence is supplied showing a specific security failure being fixed.

## Claim Boundaries

1. Classify as protocol resource-accounting hardening, not a proven vulnerability fix.
2. Do not claim a concrete liveness failure from the patch alone.
3. Do not claim malformed-input panic or remote exploitability.
4. Security relevance is limited to bounding and metering initcode processing under EIP-3860.
