---
case_id: case_20260324_8327e870e
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-24
source_refs:
  - git:8327e870e6877480eba708ab47bbf57f99791996
  - "core/vm/gas_table.go:648"
  - "core/vm/operations_acl.go:424"
  - "core/parallel_state_processor.go:105"
  - "core/vm/operations_acl.go:403"
bug_class: gas-accounting-ordering
impact_type:
  - resource-accounting
  - protocol-resource-control
confidence: medium
tags:
  - evm
  - gas-accounting
  - eip-8037
  - resource-control
  - out-of-gas-ordering
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes EIP-8037 gas accounting in SSTORE and CALL-family paths so regular gas is charged before state gas, and adjusts parallel receipt aggregation to separate execution cumulative gas from regular/state gas totals. The comments explicitly mention preventing reservoir inflation, but the provided evidence does not establish a concrete vulnerability, exploit path, denial of service, economic impact, or consensus failure.

## Observed Patch Facts

1. In `core/vm/gas_table.go`, the patch replaces `// EIP-8037: Charge state gas first (before regular gas), matching the` with `// EIP-8037: Return both regular and state gas. The interpreter`.

2. In `core/vm/operations_acl.go`, the patch replaces `// Charge state gas directly before callGas computation. State gas that` with `// Compute and charge state gas (new account creation) AFTER regular gas.`.

3. In `core/parallel_state_processor.go`, the patch replaces `blockGas += result.blockGas` with `sumRegular += result.txRegular`.

4. In `core/vm/operations_acl.go`, the patch replaces `// Early OOG check before stateful operations.` with `// Charge intrinsic cost directly (regular gas). This must happen`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/state_transition.go`, `core/vm/gascosts.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/interpreter.go`, `core/vm/instructions_test.go`. The strongest project-level identifiers around this patch are `result`, `state`, `GasCosts`, and `regular`. Nearby tests or test-like files include `core/vm/contracts_fuzz_test.go`, `core/state/statedb_fuzz_test.go`.

## Before/After Behavior

Before the patch, the SSTORE create-slot path directly charged state gas inside the gas calculation function and then returned only the regular gas cost. After the patch, it returns both regular and state gas as `GasCosts`, with comments saying the interpreter charges regular gas before state gas. Before the patch, the CALL-family EIP-8037 helper used a regular-gas comparison and state-gas handling before later call gas computation. After the patch, it charges intrinsic regular gas with `contract.UseGas(...)` before computing and charging state gas. The parallel state processor changed from accumulating `blockGas` for receipt cumulative gas to separately accumulating regular gas, state gas, and receipt execution gas.

# Root Cause

The supported root cause is inconsistent EIP-8037 gas accounting order and responsibility boundaries: some paths performed or prepared state-gas accounting before the regular-gas charge that the patched comments identify as the intended out-of-gas guard. A security root cause is not proven by the supplied evidence.

## Walkthrough

1. In `core/vm/gas_table.go`, the SSTORE storage-slot creation case previously charged state gas directly before returning the regular gas cost.

2. The patched SSTORE path returns a combined `GasCosts` value containing both regular and state gas instead of mutating gas state locally.

3. In `core/vm/operations_acl.go`, the CALL-family EIP-8037 path now charges intrinsic regular gas via `contract.UseGas(...)` before computing state gas for new account creation.

4. Patch comments state this ordering prevents reservoir inflation and makes the regular-gas charge the out-of-gas guard before stateful operations.

5. In `core/parallel_state_processor.go`, receipt cumulative gas is now tracked separately from per-dimension regular and state gas totals.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/gas_table.go | 648 | SSTORE EIP-8037 storage-slot creation gas calculation now returns both regular and state gas instead of directly charging state gas first |
| core/vm/operations_acl.go | 403 | CALL-family EIP-8037 path charges intrinsic regular gas before computing or charging state gas |
| core/vm/operations_acl.go | 424 | CALL-family state gas for new account creation is computed and charged after regular gas handling |
| core/parallel_state_processor.go | 105 | Parallel processor updates cumulative receipt gas and per-dimension regular/state gas aggregation |

## Code Snippets

## Snippet 1

Context: `core/vm/gas_table.go:648` (changes persisted or aggregate state handling)

Before
```go
if original == current {
		if original == (common.Hash{}) { // create slot (2.1.1)
			// EIP-8037: Charge state gas first (before regular gas), matching the
			// spec's charge_state_gas → charge_gas ordering. This ensures that
			// state_gas_used is recorded even if the subsequent regular gas charge
			// fails with OOG.
			stateGas := GasCosts{StateGas: params.StorageCreationSize * evm.Context.CostPerGasByte}
			if contract.Gas.Underflow(stateGas) {
```
After
```go
if original == current {
		if original == (common.Hash{}) { // create slot (2.1.1)
			// EIP-8037: Return both regular and state gas. The interpreter
			// charges regular gas before state gas, preventing reservoir
			// inflation when the regular charge OOGs.
			return GasCosts{
				RegularGas: cost.RegularGas + params.SstoreResetGasEIP2200 - params.ColdSloadCostEIP2929,
				StateGas:   params.StorageCreationSize * evm.Context.CostPerGasByte,
```

## Snippet 2

Context: `core/vm/operations_acl.go:424` (changes a sensitive control or state-update path)

Before
```go
}

		// Charge state gas directly before callGas computation. State gas that
		// spills to regular gas must reduce the gas available for callGasTemp.
		if stateGas.StateGas > 0 {
			stateGasCost := GasCosts{StateGas: stateGas.StateGas}
```
After
```go
}

		// Compute and charge state gas (new account creation) AFTER regular gas.
		stateGas, err := stateGasFunc(evm, contract, stack, mem, memorySize)
		if err != nil {
			return GasCosts{}, err
		}
		if stateGas.StateGas > 0 {
```

## Snippet 3

Context: `core/parallel_state_processor.go:105` (changes bounds, limits, or capacity handling)

Before
```go
var allReceipts []*types.Receipt
	for _, result := range results {
		blockGas += result.blockGas
		execGas += result.execGas
		result.receipt.CumulativeGasUsed = blockGas
		if blockGas > header.GasLimit {
			return &ProcessResultWithMetrics{
				ProcessResult: &ProcessResult{Error: fmt.Errorf("gas limit exceeded")},
```
After
```go
var allReceipts []*types.Receipt
	for _, result := range results {
		sumRegular += result.txRegular
		sumState += result.txState
		cumulativeReceipt += result.execGas
		result.receipt.CumulativeGasUsed = cumulativeReceipt
		allLogs = append(allLogs, result.receipt.Logs...)
		allReceipts = append(allReceipts, result.receipt)
```

## Snippet 4

Context: `core/vm/operations_acl.go:403` (changes a sensitive control or state-update path)

Before
```go
return GasCosts{}, err
		}
		// Early OOG check before stateful operations.
		if contract.Gas.RegularGas < intrinsicCost {
			return GasCosts{}, ErrOutOfGas
		}

		// Compute state gas (new account creation as state gas).
```
After
```go
return GasCosts{}, err
		}

		// Charge intrinsic cost directly (regular gas). This must happen
		// BEFORE state gas to prevent reservoir inflation, and also serves
		// as the OOG guard before stateful operations.
		if !contract.UseGas(GasCosts{RegularGas: intrinsicCost}, evm.Config.Tracer, tracing.GasChangeCallOpCode) {
			return GasCosts{}, ErrOutOfGas
```

# Fix Pattern

Centralize or defer gas mutation so helpers return combined regular/state costs, then enforce regular-gas charging before state-gas accounting. Keep receipt execution gas separate from per-dimension block gas aggregation.

## How It Was Fixed

The patch removes direct state-gas precharging from the SSTORE gas table path, charges CALL intrinsic regular gas before state gas, computes state gas afterward, and separates cumulative receipt gas from regular/state gas totals in parallel post-processing.

# Why It Matters

1. The changed code is in EVM gas accounting paths.

2. Patch comments explicitly identify reservoir inflation as the condition being avoided.

3. Incorrect gas accounting can affect protocol execution behavior.

4. The evidence does not show that the issue was exploitable or security-impacting.

# Evidence Notes

The strongest evidence is the added comments in `gas_table.go` and `operations_acl.go` stating that regular gas should be charged before state gas to prevent reservoir inflation and act as an out-of-gas guard. The commit subject is generic rebasing work, and the provided hunks do not prove attackability, consensus divergence, denial of service, or other concrete vulnerability impact. The parallel processor hunk supports an accounting correction but not a security claim by itself. Protocol security invariant: For EIP-8037 two-dimensional gas accounting, regular gas and state gas must be charged in the intended order, with regular-gas out-of-gas handling occurring before state-gas accounting that the patch comments describe as able to inflate a reservoir. Verification notes: The patch does not prove remote exploitability or transaction-level attack mechanics. The evidence does not show whether reservoir inflation could be used for consensus divergence, denial of service, or economic abuse. The commit subject suggests rebasing cleanup, so intent as a security fix is not established by metadata alone. The provided hunks do not show the final block gas-limit validation logic after per-dimension aggregation. Downgraded from likely security-hardening to unclear because the vulnerability thesis is not established. Kept the subsystem as EVM gas accounting because the changed files and comments directly support that scope. Changed bug class from state corruption to gas-accounting-ordering because no persisted state corruption is shown. Set `keep_in_security_corpus` to false under the rule for security-relevant but unproven vulnerability evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting-ordering`
Final impact type: `resource-accounting, protocol-resource-control`
Final confidence: `medium`
Final tags: `evm, gas-accounting, eip-8037, resource-control, out-of-gas-ordering`

The evidence supports a conservative security-hardening classification, not a confirmed security fix. The changed EVM gas-accounting paths explicitly reorder regular gas and state gas charging to prevent reservoir inflation and preserve out-of-gas guarding before stateful operations. That is security-sensitive resource-control behavior in transaction execution, but the supplied patch does not prove an exploit path, consensus failure, denial of service, or concrete economic impact.

## Security Evidence

1. Patch comments explicitly state the new ordering prevents reservoir inflation when regular gas charging OOGs.
2. CALL-family logic now charges intrinsic regular gas before computing or charging state gas and describes this as the OOG guard before stateful operations.
3. SSTORE EIP-8037 logic stops directly precharging state gas and returns combined regular/state gas for interpreter-ordered charging.
4. The touched code is in EVM gas accounting and transaction execution, a protocol-critical resource-control path.

## Missing Evidence

1. No concrete attacker-controlled transaction sequence is shown.
2. No proof of consensus divergence, denial of service, or economic exploitation is provided.
3. Commit metadata says generic rebasing issues rather than a security fix.
4. The parallel receipt aggregation change supports accounting correction but not security impact by itself.

## Claim Boundaries

1. Classify as hardening of gas-accounting invariants, not proven state corruption.
2. Do not claim confirmed vulnerability or exploitability from the supplied evidence.
3. Do not infer consensus failure or network-wide impact without additional evidence.
4. Keep scope limited to EIP-8037 regular/state gas ordering and OOG/resource-control behavior.
