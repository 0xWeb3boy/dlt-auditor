---
case_id: case_20230301_71d7ca3337
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-03-01
source_refs:
  - git:71d7ca33371a81eb1b29c41ab00523ccc5f10178
  - "core/tx_pool.go:678"
  - "core/state_transition.go:353"
  - "core/state_transition.go:157"
  - "core/vm/gas_table.go:348"
bug_class: protocol-resource-metering
impact_type:
  - resource-exhaustion
  - denial-of-service
confidence: medium
tags:
  - transaction-processing
  - evm
  - resource-limits
  - gas-accounting
  - initcode-size
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch implements Cortina/EIP-3860 initcode size limits and initcode word gas accounting across transaction pool validation, state transition validation, intrinsic gas calculation, and VM CREATE/CREATE2 gas calculation. The evidence supports a protocol resource-metering change, but it does not establish that the prior behavior was an exploitable vulnerability.

## Observed Patch Facts

1. In `core/tx_pool.go`, the patch adds `// Check whether the init code size has been exceeded.`.

2. In `core/state_transition.go`, the patch replaces `if rules.IsApricotPhase2 {` with `// Check whether the init code size has been exceeded.`.

3. In `core/state_transition.go`, the patch replaces `z := uint64(len(data)) - nz` with `z := dataLen - nz`.

4. In `core/vm/gas_table.go`, the patch replaces `func gasExpFrontier(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memorySi...` with `func gasCreateEip3860(evm *EVM, contract *Contract, stack *Stack, mem *Memory, memory...`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/state_processor_test.go`, `core/vm/operations_acl.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/operations_acl.go`, `core/vm/jump_table.go`. The strongest project-level identifiers around this patch are `size`, `params`, `MaxInitCodeSize`, and `uint64`.

## Before/After Behavior

Before the change, the supplied snippets do not show MaxInitCodeSize enforcement in tx pool validation or state transition, and IntrinsicGas does not show EIP-3860 initcode word gas charging. After the change, Cortina contract-creation transactions with initcode larger than params.MaxInitCodeSize are rejected in tx pool validation and state transition, IntrinsicGas charges InitCodeWordGas per initcode word for contract creation, and VM create gas accounting checks stack-derived initcode size and adds the same per-word gas cost.

# Root Cause

The pre-patch code shown lacked the newly introduced Cortina/EIP-3860 initcode size and gas metering rules in the affected paths. The provided evidence does not prove a security root cause such as a crash, consensus split, or remotely exploitable denial of service.

## Walkthrough

1. A contract-creation transaction reaches core/tx_pool.go validation.

2. The patched tx pool code rejects Cortina contract-creation transactions when tx.To() == nil and len(tx.Data()) exceeds params.MaxInitCodeSize.

3. During state transition, the patched code identifies contract creation with msg.To() == nil and rejects oversized initcode under Cortina rules.

4. IntrinsicGas now receives the activation flag and, for contract creation, adds InitCodeWordGas multiplied by the 32-byte word size of the initcode data with overflow checks.

5. The VM gas table adds gasCreateEip3860, which reads initcode size from the stack, rejects overflow or size above params.MaxInitCodeSize, and adds per-word initcode gas.

6. These changes align several execution and admission paths with the new EIP-3860 resource rule.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/tx_pool.go | 678 | rejects Cortina contract-creation transactions whose initcode data exceeds MaxInitCodeSize before mempool admission |
| core/state_transition.go | 353 | enforces the same MaxInitCodeSize consensus rule during transaction execution |
| core/state_transition.go | 157 | adds EIP-3860 intrinsic gas charging for contract creation initcode words with overflow checks |
| core/vm/gas_table.go | 348 | adds CREATE/CREATE2 initcode word gas accounting and oversized-size handling in VM gas calculation |

## Code Snippets

## Snippet 1

Context: `core/tx_pool.go:678` (changes bounds, limits, or capacity handling)

Before
```go
return fmt.Errorf("%w tx size %d > max size %d", ErrOversizedData, txSize, txMaxSize)
	}
	// Transactions can't be negative. This may never happen using RLP decoded
	// transactions but may occur if you create a transaction using the RPC.
```
After
```go
return fmt.Errorf("%w tx size %d > max size %d", ErrOversizedData, txSize, txMaxSize)
	}
	// Check whether the init code size has been exceeded.
	if pool.cortina && tx.To() == nil && len(tx.Data()) > params.MaxInitCodeSize {
		return fmt.Errorf("%w: code size %v limit %v", vmerrs.ErrMaxInitCodeSizeExceeded, len(tx.Data()), params.MaxInitCodeSize)
	}
	// Transactions can't be negative. This may never happen using RLP decoded
	// transactions but may occur if you create a transaction using the RPC.
```

## Snippet 2

Context: `core/state_transition.go:353` (changes bounds, limits, or capacity handling)

Before
```go
}

	// Set up the initial access list.
	if rules.IsApricotPhase2 {
```
After
```go
}

	// Check whether the init code size has been exceeded.
	if rules.IsCortina && contractCreation && len(st.data) > params.MaxInitCodeSize {
		return nil, fmt.Errorf("%w: code size %v limit %v", vmerrs.ErrMaxInitCodeSizeExceeded, len(st.data), params.MaxInitCodeSize)
	}

	// Set up the initial access list.
```

## Snippet 3

Context: `core/state_transition.go:157` (changes a sensitive control or state-update path)

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

## Snippet 4

Context: `core/vm/gas_table.go:348` (changes a sensitive control or state-update path)

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

# Fix Pattern

Activation-gated protocol resource metering: add size-limit validation and per-word gas accounting for contract creation initcode across relevant validation and VM gas calculation paths.

## How It Was Fixed

The patch adds MaxInitCodeSize checks in core/tx_pool.go and core/state_transition.go, extends IntrinsicGas to charge InitCodeWordGas for contract creation when EIP-3860/Cortina is active, and adds VM gas accounting for CREATE/CREATE2 initcode size and word gas with overflow handling.

# Why It Matters

1. Enforces the new Cortina/EIP-3860 initcode size rule in the shown paths.

2. Prevents oversized contract-creation initcode from being accepted into the tx pool after activation.

3. Adds initcode word gas accounting for contract creation.

4. Uses checked arithmetic in the modified gas accounting paths.

# Evidence Notes

Grounded evidence is limited to the supplied diffs in core/tx_pool.go, core/state_transition.go, and core/vm/gas_table.go. Claims of a prior panic, cryptographic issue, consensus split, or proven remotely exploitable denial of service are unsupported. The unrelated bn256 test file should not be treated as evidence for the root cause. Protocol security invariant: After Cortina/EIP-3860 activation, contract-creation initcode is limited by params.MaxInitCodeSize and charged params.InitCodeWordGas per 32-byte word in the shown admission, state transition, intrinsic gas, and VM create gas accounting paths. Verification notes: The patch does not prove a prior remotely exploitable denial of service. The patch does not show a consensus split by itself; it implements activation-gated protocol rules. The patch does not evidence a cryptographic flaw despite the unrelated bn256 test file in the commit. The patch does not prove malformed input caused a panic; added errors are ordinary validation and gas/accounting failures. The tx pool check is policy/admission hardening, while state_transition is the consensus-relevant enforcement path. No external context or repository inspection was used. The patch is best treated as protocol implementation or possible security hardening, not a confirmed vulnerability fix. Because the vulnerability thesis is not established by the provided evidence, it should not be kept in the security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-resource-metering`
Final impact type: `resource-exhaustion, denial-of-service`
Final confidence: `medium`
Final tags: `transaction-processing, evm, resource-limits, gas-accounting, initcode-size, protocol-hardening`

The supplied patch evidence does not prove a concrete exploitable vulnerability, but it does clearly add activation-gated resource controls in security-sensitive transaction execution paths: oversized contract-creation initcode is rejected in both tx pool admission and state transition, and initcode word gas is charged with overflow checks. This is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Adds MaxInitCodeSize rejection for Cortina contract-creation transactions in tx pool validation.
2. Adds the same MaxInitCodeSize enforcement during state transition, a consensus-relevant execution path.
3. Adds EIP-3860 intrinsic gas charging for contract creation initcode words.
4. Adds VM CREATE/CREATE2 gas accounting with overflow and size checks.

## Missing Evidence

1. No advisory, CVE, exploit, crash, consensus split, or incident evidence is supplied.
2. No proof that pre-patch oversized initcode caused practical node denial of service.
3. No evidence that the unrelated bn256 test case fixes a cryptographic vulnerability.

## Claim Boundaries

1. Classify as protocol resource hardening, not a confirmed vulnerability fix.
2. Do not claim a proven remote DoS or consensus failure from the patch alone.
3. Do not treat the bn256ScalarMul test addition as security evidence for this finding.
4. The supported claim is limited to stricter initcode size enforcement and gas metering after Cortina/EIP-3860 activation.
