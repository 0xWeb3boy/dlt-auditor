---
case_id: case_20210722_97aacd9b3
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2021-07-22
source_refs:
  - git:97aacd9b359035d6cfeebf186f4420ccc19c7ecc
  - "eth/tracers/api_test.go:370"
  - "core/state_processor_test.go:119"
  - "cmd/evm/testdata/12/alloc.json:1"
  - "core/state_transition.go:194"
bug_class: transaction-balance-validation
impact_type:
  - consensus-state-transition-integrity
confidence: medium
tags:
  - transaction-processing
  - eip-1559
  - balance-check
  - state-transition
  - economic-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects go-ethereum's London/EIP-1559 upfront balance check. In StateTransition.buyGas, the EIP-1559 balance requirement previously included gas_limit * gasFeeCap but omitted the transaction value. The fix adds st.value before comparing the sender balance to the required amount. This is best classified as a likely security-relevant consensus/state-transition validation fix, not as replay, signature, or cryptographic handling.

## Observed Patch Facts

1. In `eth/tracers/api_test.go`, the patch replaces `expectErr: core.ErrInsufficientFundsForTransfer,` with `expectErr: core.ErrInsufficientFunds,`.

2. In `core/state_processor_test.go`, the patch replaces `want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb7382304...` with `want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb7382304...`.

3. In `cmd/evm/testdata/12/alloc.json`, the patch adds `"0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {`.

4. In `core/state_transition.go`, the patch adds `balanceCheck.Add(balanceCheck, st.value)`.

## Project Context

The changed code sits primarily in `eth/tracers`, `cmd/evm/testdata/12`, `cmd/evm/testdata`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/tracers/tracers_test.go`, `eth/tracers/tracer_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/tracers/tracers_test.go`, `eth/tracers/tracer_test.go`. The strongest project-level identifiers around this patch are `balanceCheck`, `want`, `have`, and `expectErr`.

## Before/After Behavior

Before the patch, an EIP-1559 transaction with st.gasFeeCap set was checked only against gas_limit * gasFeeCap in buyGas, even though the transfer value had not yet been deducted. After the patch, the same check requires gas_limit * gasFeeCap + value. Tests now expect ErrInsufficientFunds and an error message showing gas * price + value rather than a later insufficient-funds-for-transfer error.

# Root Cause

The EIP-1559 balance precheck in StateTransition.buyGas was incomplete for go-ethereum's execution order: it performed the balance comparison before deducting the transfer value, but did not include that value in the upfront required balance.

## Walkthrough

1. A London/EIP-1559 transaction reaches StateTransition.buyGas with st.gasFeeCap non-nil.

2. The old code computed balanceCheck as st.msg.Gas() * st.gasFeeCap.

3. The sender balance was compared against that amount before the transaction value had been deducted.

4. Because st.value was omitted, the precheck did not require the sender to cover both maximum gas liability and transferred value.

5. The patch adds balanceCheck.Add(balanceCheck, st.value) before the balance comparison.

6. State processor and tracer tests were updated to expect the earlier ErrInsufficientFunds path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 194 | core London/EIP-1559 transaction precheck now requires sender balance >= gas * gasFeeCap + value |
| core/state_processor_test.go | 119 | state processor regression expectation for insufficient funds including gas cap liability plus transferred value |
| eth/tracers/api_test.go | 370 | trace-call test adjusted to expect core insufficient funds from the earlier corrected validation path |
| cmd/evm/testdata/12/alloc.json | 1 | EVM test fixture for low-balance transaction validation scenario |

## Code Snippets

## Snippet 1

Context: `eth/tracers/api_test.go:370` (changes a sensitive control or state-update path)

Before
```go
Tracer: &tracer,
			},
			expectErr: core.ErrInsufficientFundsForTransfer,
			expect:    nil,
		},
```
After
```go
Tracer: &tracer,
			},
			expectErr: core.ErrInsufficientFunds,
			expect:    nil,
		},
```

## Snippet 2

Context: `core/state_processor_test.go:119` (changes a sensitive control or state-update path)

Before
```go
makeTx(0, common.Address{}, big.NewInt(1000000000000000000), params.TxGas, big.NewInt(875000000), nil),
				},
				want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb73823042dd0638d74]: insufficient funds for transfer: address 0x71562b71999873DB5b286dF957af199Ec94617F7",
			},
			{ // ErrInsufficientFunds
```
After
```go
makeTx(0, common.Address{}, big.NewInt(1000000000000000000), params.TxGas, big.NewInt(875000000), nil),
				},
				want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb73823042dd0638d74]: insufficient funds for gas * price + value: address 0x71562b71999873DB5b286dF957af199Ec94617F7 have 1000000000000000000 want 1000018375000000000",
			},
			{ // ErrInsufficientFunds
```

## Snippet 3

Context: `cmd/evm/testdata/12/alloc.json:1` (changes signature or replay validation logic)

Before
```text
(no before snippet captured)
```
After
```text
{
    "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {
        "balance" : "84000000",
        "code" : "0x",
        "nonce" : "0x00",
        "storage" : {
            "0x00" : "0x00"
        }
```

## Snippet 4

Context: `core/state_transition.go:194` (changes aggregate state or economic accounting)

Before
```go
balanceCheck = new(big.Int).SetUint64(st.msg.Gas())
		balanceCheck = balanceCheck.Mul(balanceCheck, st.gasFeeCap)
	}
	if have, want := st.state.GetBalance(st.msg.From()), balanceCheck; have.Cmp(want) < 0 {
```
After
```go
balanceCheck = new(big.Int).SetUint64(st.msg.Gas())
		balanceCheck = balanceCheck.Mul(balanceCheck, st.gasFeeCap)
		balanceCheck.Add(balanceCheck, st.value)
	}
	if have, want := st.state.GetBalance(st.msg.From()), balanceCheck; have.Cmp(want) < 0 {
```

# Fix Pattern

Include all not-yet-deducted liabilities in upfront transaction affordability checks before comparing sender balance against the required amount.

## How It Was Fixed

The implementation adds st.value to balanceCheck inside the st.gasFeeCap != nil branch of StateTransition.buyGas. Regression expectations and EVM test fixtures were adjusted for the low-balance EIP-1559 case.

# Why It Matters

1. Maintains the EIP-1559 sender-balance validity rule.

2. Prevents underfunded transactions from passing the shown upfront validation path.

3. Affects consensus-sensitive state transition logic.

4. No concrete exploit, fund theft, or chain split is proven by the supplied evidence.

# Evidence Notes

The strongest evidence is core/state_transition.go line 194, where balanceCheck.Add(balanceCheck, st.value) was added. core/state_processor_test.go line 119 changes the expected failure from insufficient funds for transfer to insufficient funds for gas * price + value with explicit have and want balances. eth/tracers/api_test.go line 370 updates the expected error to core.ErrInsufficientFunds. cmd/evm/testdata/12/alloc.json appears to be a supporting low-balance fixture, not the root cause. Claims about replay protection, signature validation, cryptography, or concrete exploitability are unsupported. Protocol security invariant: For London/EIP-1559 transactions, the sender balance checked before state mutation must cover the maximum gas liability, gas_limit * gasFeeCap, plus the transaction value when that value has not yet been deducted. Verification notes: No evidence that this is a replay or signature-validation bug. No cryptographic primitive or transaction signing logic is shown as changed. No concrete exploitability, chain split, or fund theft scenario is proven by the patch alone. Tracer files appear to reflect expected error behavior, not the root cause subsystem. Legacy non-EIP-1559 balance validation is not shown to be changed. Verified only against the provided commit message, mapper output, draft, and extracted diff evidence. No independent file inspection, command execution, or external context was used. Security classification is likely because the changed logic is transaction validity/state transition code, but exploit impact is not demonstrated in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-balance-validation`
Final impact type: `consensus-state-transition-integrity`
Final confidence: `medium`
Final tags: `transaction-processing, eip-1559, balance-check, state-transition, economic-accounting`

The evidence supports a security-sensitive hardening/fix in go-ethereum's London/EIP-1559 transaction validation path: the sender balance precheck now includes both gas_limit * gasFeeCap and transaction value before state mutation. This is not supported as replay, signature, or cryptographic validation, and the patch alone does not prove a concrete exploit, fund theft, or chain split. It is appropriate to keep as security-hardening rather than a high-confidence security-fix.

## Security Evidence

1. core/state_transition.go adds st.value to the EIP-1559 balanceCheck before comparing sender balance.
2. Commit message states EIP-1559 mandates checking sufficient balance for gas * gasFeeCap and explains go-ethereum needed to add value explicitly because balance had not yet been updated.
3. Tests now expect ErrInsufficientFunds with an explicit gas * price + value requirement instead of a later insufficient-funds-for-transfer path.
4. The changed code is in core transaction state transition logic, a consensus/economic-accounting-sensitive path.

## Missing Evidence

1. No evidence of replay, signature, or cryptographic validation changes.
2. No demonstrated exploit scenario, fund theft, denial of service, or chain split from the supplied patch alone.
3. No security advisory, vulnerability identifier, or attacker-controlled trigger analysis is provided.
4. The evidence does not prove whether later validation would always or only sometimes reject the underfunded transaction.

## Claim Boundaries

1. Classify as EIP-1559 transaction balance validation, not replay or signature validation.
2. Treat the impact as consensus/state-transition integrity risk, not proven direct asset theft.
3. Keep confidence at medium because security relevance is plausible from the subsystem and invariant, but concrete exploitability is not shown.
4. Tracer and fixture changes are supporting regression evidence, not independent root-cause evidence.
