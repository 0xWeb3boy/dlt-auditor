---
case_id: case_20230111_793f0f9ec
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
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
bug_class: resource-control-hardening
impact_type:
  - resource-exhaustion
confidence: medium
tags:
  - resource-control
  - consensus-rules
  - initcode
  - evm
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports implementation of the Shanghai EIP-3860 rules for initcode size limits and metering. It does not establish that the patch fixes a preexisting vulnerability; this reads as protocol feature enablement and consensus-rule compliance work.

## Observed Patch Facts

1. In `core/state_transition.go`, the patch replaces `// - prepare accessList(post-berlin)` with `// Check whether the init code size has been exceeded.`.

2. In `core/state_transition.go`, the patch replaces `z := uint64(len(data)) - nz` with `z := dataLen - nz`.

3. In `core/vm/gas_table.go`, the patch replaces `func gasExpFrontier(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi...` with `func gasCreateEip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memory...`.

4. In `core/state_transition.go`, the patch replaces `// NewStateTransition initialises and returns a new state transition object.` with `// toWordSize returns the ceiled word size required for init code payment calculation.`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/vm/interface.go`, `core/vm/instructions_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/interface.go`, `core/vm/instructions_test.go`. The strongest project-level identifiers around this patch are `size`, `params`, `uint64`, and `math`.

## Before/After Behavior

Before the patch, the shown paths did not enforce a Shanghai-specific initcode size cap and did not add the EIP-3860 per-word initcode charge in intrinsic gas or the new CREATE-path helper. After the patch, oversized initcode is rejected for Shanghai contract-creation transactions, intrinsic gas includes initcode word charges, and CREATE execution uses bounded initcode metering.

# Root Cause

No accidental defect is demonstrated by the provided evidence. The prior behavior appears to reflect the pre-Shanghai ruleset, and the patch adds new fork-gated protocol constraints rather than correcting a proven vulnerability.

## Walkthrough

1. `TransitionDb()` gains a Shanghai-gated check that rejects contract-creation transactions when `len(st.data) > params.MaxInitCodeSize`.

2. `IntrinsicGas(...)` now computes `dataLen` once and, for contract creation under EIP-3860, adds `params.InitCodeWordGas` per rounded-up 32-byte word.

3. `toWordSize(size uint64)` is introduced to round safely for initcode metering.

4. `gasCreateEip3860(...)` is added in `core/vm/gas_table.go` to meter CREATE-family initcode with overflow checks and the same size bound.

5. These changes align transaction-level and VM-level behavior with the commit message's stated EIP-3860 enablement scope.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 338 | pre-execution validation rejects contract-creation transactions whose initcode exceeds the Shanghai size limit |
| core/state_transition.go | 149 | intrinsic gas accounting adds per-word initcode metering for contract-creation transactions under EIP-3860 |
| core/state_transition.go | 170 | word-size helper used to safely compute initcode metering units |
| core/vm/gas_table.go | 303 | CREATE/CREATE2 gas calculation applies bounded initcode metering inside EVM execution |

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

Fork-gated protocol rule implementation: add new resource limits and deterministic gas metering across all relevant execution layers, with explicit overflow handling.

## How It Was Fixed

The patch implements EIP-3860 by adding a Shanghai-only initcode size rejection in state transition, adding per-word initcode gas in intrinsic gas accounting, and introducing CREATE-path metering with bounded arithmetic and size checks.

# Why It Matters

1. Prevents mislabeling protocol-upgrade work as a vulnerability fix.

2. Shows the exact resource-control points changed for contract creation.

3. The evidence is security-relevant in subject matter, but not proof of a previously exploitable bug.

# Evidence Notes

Direct support comes from `core/state_transition.go` and `core/vm/gas_table.go`. The new code explicitly rejects oversized initcode under Shanghai, adds `InitCodeWordGas` in `IntrinsicGas(...)`, introduces `toWordSize(...)`, and adds `gasCreateEip3860(...)` with overflow and size checks. The commit message explicitly says it implements EIP-3860 as part of the Shanghai fork. Nothing in the provided hunks proves a prior crash, auth bypass, memory-safety flaw, or unintended acceptance bug outside the new protocol baseline. Protocol security invariant: Under Shanghai/EIP-3860, contract creation must enforce a maximum initcode size and charge additional gas per 32-byte word of initcode in both transaction admission and CREATE-family execution paths. Verification notes: The patch does not by itself prove an exploitable denial-of-service bug existed before Shanghai activation. The evidence does not show memory corruption, authentication failure, fund loss, or privilege escalation. The commit appears to implement a scheduled consensus change, not to remove an accidental panic path or serialization bug. The provided hunks do not prove whether any network accepted oversize initcode before this fork rule by mistake versus by previous protocol design. The commit message frames the change as EIP-3860 enablement, not bug remediation. The evidence shows added limits and metering, not removal of a demonstrated exploit path. `keep_in_security_corpus` should remain false because the supplied proof supports protocol implementation, not a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-control-hardening`
Final impact type: `resource-exhaustion`
Final confidence: `medium`
Final tags: `resource-control, consensus-rules, initcode, evm`

The patch is not presented as a remediation for a known exploitable defect, but it does clearly add security-relevant resource controls in a critical execution path: a Shanghai-gated initcode size limit, extra initcode metering, and overflow-bounded CREATE gas calculation. That is stronger than ordinary feature work, yet weaker than a confirmed security fix, so the most defensible classification from the patch alone is security hardening.

## Security Evidence

1. Adds an explicit max initcode size check before contract creation execution.
2. Adds per-word initcode gas charging in intrinsic gas calculation under EIP-3860.
3. Introduces CREATE-path gas logic with overflow checks and bounded size handling.
4. Changes occur in transaction processing and EVM gas accounting, which are security-sensitive resource-control paths.

## Missing Evidence

1. No proof of a preexisting vulnerability or exploit is shown in the patch.
2. No incident, CVE, advisory, or bug report ties the change to an actual attack.
3. The commit message frames the work as Shanghai/EIP-3860 enablement rather than vulnerability remediation.

## Claim Boundaries

1. Supported claim: the commit hardens initcode resource limits and metering.
2. Not supported: a confirmed exploitable denial-of-service bug existed before this change.
3. Not supported: this patch alone proves fund loss, auth bypass, memory corruption, or privilege escalation.
