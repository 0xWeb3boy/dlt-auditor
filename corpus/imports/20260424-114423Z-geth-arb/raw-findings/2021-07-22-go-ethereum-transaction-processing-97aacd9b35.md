---
case_id: case_20210722_97aacd9b35
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2021-07-22
source_refs:
  - git:97aacd9b359035d6cfeebf186f4420ccc19c7ecc
  - "eth/tracers/api_test.go:370"
  - "core/state_processor_test.go:119"
  - "cmd/evm/testdata/12/alloc.json:1"
  - "core/state_transition.go:194"
bug_class: protocol-balance-validation
impact_type:
  - protocol-invariant-enforcement
  - economic-accounting-validation
tags:
  - infrastructure
  - transaction-processing
  - eip-1559
  - protocol-validation
  - balance-check
  - economic-accounting
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects go-ethereum's London/EIP-1559 sender balance precheck in `StateTransition.buyGas` by adding `st.value` to the EIP-1559 `balanceCheck` before comparing it with the sender balance. The evidence supports a protocol-validity hardening in the core transaction state transition path. It does not support the earlier replay, signature-validation, or cryptographic-change framing, and it does not prove a concrete exploit or demonstrated consensus split.

## Observed Patch Facts

1. In `eth/tracers/api_test.go`, the patch replaces `expectErr: core.ErrInsufficientFundsForTransfer,` with `expectErr: core.ErrInsufficientFunds,`.

2. In `core/state_processor_test.go`, the patch replaces `want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb7382304...` with `want: "could not apply tx 0 [0x98c796b470f7fcab40aaef5c965a602b0238e1034cce6fb7382304...`.

3. In `cmd/evm/testdata/12/alloc.json`, the patch adds `"0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {`.

4. In `core/state_transition.go`, the patch adds `balanceCheck.Add(balanceCheck, st.value)`.

## Project Context

The changed code sits primarily in `eth/tracers`, `cmd/evm/testdata/12`, `cmd/evm/testdata`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/tracers/tracers_test.go`, `eth/tracers/tracer_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/tracers/tracers_test.go`, `eth/tracers/tracer_test.go`. The strongest project-level identifiers around this patch are `balanceCheck`, `want`, `have`, and `expectErr`.

## Before/After Behavior

Before the patch, the EIP-1559 branch in `core/state_transition.go` checked the sender balance against `gas limit * gasFeeCap` only. Since go-ethereum had not yet deducted the transaction value at that point, the upfront balance check omitted the transfer value. After the patch, `balanceCheck.Add(balanceCheck, st.value)` makes the comparison require `gas limit * gasFeeCap + value`. Tests were updated to expect `ErrInsufficientFunds` with a wanted amount including both gas liability and value, rather than a later transfer-specific insufficient-funds error.

# Root Cause

The implementation applied the EIP-1559 balance rule at a different point in state-transition ordering than the EIP pseudocode assumes. The pseudocode assumes value has already been deducted when the gas-fee-cap check occurs, but go-ethereum performs this check before value deduction, so the value component had to be added explicitly.

## Walkthrough

1. A transaction reaches `StateTransition.buyGas` in the core state transition path.

2. For EIP-1559 transactions, identified by `st.gasFeeCap != nil`, the code computes `balanceCheck` from the gas limit and gas fee cap.

3. Before the fix, that EIP-1559 `balanceCheck` did not include `st.value`.

4. The sender balance was compared against the incomplete requirement using `st.state.GetBalance(st.msg.From())`.

5. The patch adds `balanceCheck.Add(balanceCheck, st.value)` before the comparison.

6. Regression expectations were changed so transactions lacking balance for both value and maximum gas liability fail at the upfront insufficient-funds check.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 194 | core transaction state transition balance precheck for London/EIP-1559 gas fee cap and transfer value |
| core/state_processor_test.go | 119 | state processor regression expectation for rejecting transactions lacking gas fee cap plus value balance |
| eth/tracers/api_test.go | 370 | trace call error expectation aligned with upfront insufficient funds validation |
| cmd/evm/testdata/12/alloc.json | 1 | EVM fixture account balance for regression coverage |

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

When protocol validity checks run before related state mutations, compute the validation predicate against the state as it exists at that point in the implementation. Here, the upfront EIP-1559 balance check must include both value and `gasLimit * gasFeeCap`.

## How It Was Fixed

The implementation change is a focused one-line fix in `core/state_transition.go`: after calculating EIP-1559 `balanceCheck` as `st.msg.Gas() * st.gasFeeCap`, the code adds `st.value` before comparing the sender balance with the required amount. Tests and EVM fixtures were updated to cover the stricter rejection path.

# Why It Matters

1. Enforces the supplied EIP-1559 balance invariant in the core transaction path.

2. Aligns validation with go-ethereum's actual ordering of checks and value deduction.

3. Prevents transactions from passing the upfront EIP-1559 balance precheck with only gas-fee-cap coverage.

4. Does not establish replay, signature validation, or cryptographic vulnerability claims.

# Evidence Notes

The strongest evidence is the added `balanceCheck.Add(balanceCheck, st.value)` line in `core/state_transition.go` inside `StateTransition.buyGas`. Supporting evidence comes from updated expectations in `core/state_processor_test.go` and `eth/tracers/api_test.go`, plus the added `cmd/evm/testdata/12/alloc.json` fixture. The commit message states the EIP-1559 rule and explains the ordering mismatch. The evidence does not show a concrete exploit, remote attack path, persisted invalid transaction, or actual consensus split, so the finding should be treated as likely protocol/security hardening rather than a confirmed vulnerability fix. Protocol security invariant: Under London/EIP-1559 transaction rules, the sender must have enough balance to cover the transfer value plus the maximum gas liability, computed as value + gas limit * gasFeeCap. Because go-ethereum performs the balance check before deducting value from state, the value must be included explicitly in that upfront check. Verification notes: No replay or signature-validation bug is shown by the patch evidence. No concrete exploitability, remote attack path, or demonstrated consensus split is proven here. The evidence shows stricter London balance validation, not cryptographic logic changes. The patch may change rejection timing and error classification; it does not prove that invalid transactions were successfully persisted before the fix. Downgraded the bug class away from replay or signature validation. Kept the subsystem focused on core state transition rather than tracers or fixtures. Kept confidence at medium because the protocol-rule mismatch is clear, but concrete exploitability is not shown. Treated helper testdata as regression support, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-balance-validation`
Final impact type: `protocol-invariant-enforcement, economic-accounting-validation`
Final tags: `infrastructure, transaction-processing, eip-1559, protocol-validation, balance-check, economic-accounting`

The evidence supports retaining this as security hardening: the patch tightens a consensus/protocol-sensitive transaction balance check for London/EIP-1559 by requiring sender balance to cover both value and gas limit multiplied by gasFeeCap before state transition proceeds. The patch does not substantiate replay, signature-validation, cryptographic, or request-forgery claims, and it does not prove a concrete exploit or consensus split.

## Security Evidence

1. Core state transition code adds st.value to the EIP-1559 balanceCheck before comparing sender balance.
2. Commit message states EIP-1559 requires sufficient balance for gas * gasFeeCap and explains go-ethereum's ordering mismatch.
3. Regression expectations change from transfer-only insufficient funds to insufficient funds for gas * price + value.
4. The affected code is in transaction state processing, a protocol-sensitive path.

## Missing Evidence

1. No demonstrated exploit, attack transaction, or chain impact is shown.
2. No evidence of replay, signature validation, or cryptographic logic changes is present.
3. No proof that invalid transactions were accepted into finalized state or caused a consensus split.
4. Patch evidence suggests stricter rejection timing but not a concrete vulnerability disclosure.

## Claim Boundaries

1. Classify as protocol/economic validation hardening, not replay or signature validation.
2. Do not claim request forgery, replay, or cryptographic impact.
3. Do not claim confirmed exploitability or real-world exploitation.
4. Do not infer consensus failure beyond the shown EIP-1559 balance invariant correction.
