---
case_id: case_20260203_a5393933f
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2026-02-03
source_refs:
  - git:a5393933f5e8c0d5be2d493b6624a6589bec155a
  - "src/herder/TransactionQueue.cpp:503"
  - "src/transactions/TransactionFrame.cpp:311"
  - "src/herder/TxSetFrame.cpp:1757"
  - "src/transactions/FeeBumpTransactionFrame.cpp:475"
bug_class: transaction-validation-hardening
impact_type:
  - invalid-transaction-rejection
confidence: medium
tags:
  - blockchain-core
  - consensus
  - transaction-validation
  - soroban
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds validateHostFn() checks to Soroban transaction admission and related transaction-set validation paths. This is plausibly security relevant because it affects protocol validation, but the supplied hunks do not show the full invalid condition or demonstrate exploitability, denial of service, fund loss, or consensus divergence. Treat this as unclear validation hardening rather than a confirmed vulnerability fix.

## Observed Patch Facts

1. In `src/herder/TransactionQueue.cpp`, the patch replaces `return AddResult(TransactionQueue::AddResultCode::ADD_STATUS_PENDING,` with `if (!tx->validateHostFn())`.

2. In `src/transactions/TransactionFrame.cpp`, the patch replaces `TransactionFrame::validateSorobanMemo() const` with `TransactionFrame::validateHostFn() const`.

3. In `src/herder/TxSetFrame.cpp`, the patch replaces `return txsAreValid(app, lowerBoundCloseTimeOffset,` with `auto invalid = TxSetUtils::getInvalidTxList(`.

4. In `src/transactions/FeeBumpTransactionFrame.cpp`, the patch replaces `int64_t` with `bool`.

## Project Context

The changed code sits primarily in `src/herder`, `src/transactions`, which anchors the finding in the `consensus` area of the project. Historical context from `src/herder/HerderImpl.cpp`, `src/transactions/TransactionFrameBase.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/herder/HerderImpl.cpp`, `src/transactions/TransactionFrameBase.h`. The strongest project-level identifiers around this patch are `validateHostFn`, `const`, `TransactionQueue::AddResultCode::ADD_STATUS_ERROR`, and `TransactionFrame::validateHostFn`. Nearby tests or test-like files include `src/herder/test/HerderTests.cpp`, `src/transactions/test/TransactionTestFrame.h`.

## Before/After Behavior

Before the patch, the shown TransactionQueue::canAdd path could return ADD_STATUS_PENDING after earlier Soroban checks without the newly shown validateHostFn() gate. After the patch, validateHostFn() failure returns ADD_STATUS_ERROR with txSOROBAN_INVALID. TransactionFrame gains validateHostFn(), FeeBumpTransactionFrame delegates validateHostFn() to its inner transaction, and TxSetPhaseFrame::checkValid changes to accept only when TxSetUtils::getInvalidTxList(...) is empty.

# Root Cause

The grounded root cause is inconsistent or previously absent host-function validation in the shown queue admission and wrapper transaction paths. The evidence does not prove the exact malformed host-function case or that the gap was exploitable.

## Walkthrough

1. A transaction reaches TransactionQueue::canAdd after earlier Soroban memo or muxed-account validation.

2. The pre-patch evidence shows the path returning ADD_STATUS_PENDING without a validateHostFn() check at that point.

3. The patch adds tx->validateHostFn() and rejects failure as txSOROBAN_INVALID.

4. TransactionFrame::validateHostFn() is added and applies only to Soroban transactions in the shown excerpt.

5. FeeBumpTransactionFrame::validateHostFn() delegates to the inner transaction, preserving inner validation through the wrapper.

6. TxSetPhaseFrame::checkValid now checks TxSetUtils::getInvalidTxList(...) and requires it to be empty.

7. The changes improve validation consistency, but the provided evidence does not establish a concrete security impact.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/herder/TransactionQueue.cpp | 503 | queue admission now rejects Soroban transactions whose host function validation fails |
| src/transactions/TransactionFrame.cpp | 311 | defines TransactionFrame::validateHostFn for Soroban transaction host-function validation |
| src/transactions/FeeBumpTransactionFrame.cpp | 475 | delegates fee-bump host-function validation to the inner transaction |
| src/herder/TxSetFrame.cpp | 1757 | transaction set phase validity now checks invalid transactions via TxSetUtils::getInvalidTxList |

## Code Snippets

## Snippet 1

Context: `src/herder/TransactionQueue.cpp:503` (changes a consensus- or validator-sensitive branch)

Before
```cpp
}

    return AddResult(TransactionQueue::AddResultCode::ADD_STATUS_PENDING,
                     tx->createValidationSuccessResult());
```
After
```cpp
}

    if (!tx->validateHostFn())
    {
        return AddResult(TransactionQueue::AddResultCode::ADD_STATUS_ERROR, *tx,
                         txSOROBAN_INVALID, diagnosticEvents.finalize());
    }
```

## Snippet 2

Context: `src/transactions/TransactionFrame.cpp:311` (changes a sensitive control or state-update path)

Before
```cpp
}

bool
TransactionFrame::validateSorobanMemo() const
```
After
```cpp
}

bool
TransactionFrame::validateHostFn() const
{
    if (!isSoroban())
    {
        return true;
```

## Snippet 3

Context: `src/herder/TxSetFrame.cpp:1757` (changes a sensitive control or state-update path)

Before
```cpp
}

    return txsAreValid(app, lowerBoundCloseTimeOffset,
                       upperBoundCloseTimeOffset);
}
```
After
```cpp
}

    auto invalid = TxSetUtils::getInvalidTxList(
        *this, app, lowerBoundCloseTimeOffset, upperBoundCloseTimeOffset);
    return invalid.empty();
}
```

## Snippet 4

Context: `src/transactions/FeeBumpTransactionFrame.cpp:475` (changes a sensitive control or state-update path)

Before
```cpp
}

int64_t
FeeBumpTransactionFrame::getFullFee() const
```
After
```cpp
}

bool
FeeBumpTransactionFrame::validateHostFn() const
{
    return mInnerTx->validateHostFn();
}
```

# Fix Pattern

Add explicit validation at transaction admission and transaction-set validity boundaries, and delegate wrapper validation to the wrapped transaction.

## How It Was Fixed

The patch introduces validateHostFn() on transaction frames, calls it from TransactionQueue::canAdd, returns txSOROBAN_INVALID on failure, delegates fee-bump validation to the inner transaction, and changes txset phase validity to use explicit invalid-transaction detection.

# Why It Matters

1. Protocol validation paths should agree on which Soroban transactions are invalid.

2. Fee-bump wrappers should not weaken validation of the inner transaction.

3. Missing validation can be security relevant in consensus software, but impact is not shown here.

# Evidence Notes

Evidence supports a validation-path change in TransactionQueue.cpp, TransactionFrame.cpp, FeeBumpTransactionFrame.cpp, and TxSetFrame.cpp. Unsupported claims removed: confirmed consensus split, exploitable malformed host function, denial of service, fund loss, or remote attackability. The full validateHostFn() body and exact invalid cases are not provided. Protocol security invariant: Soroban transactions, including fee-bump-wrapped transactions, should pass host-function validation consistently before queue admission or transaction-set acceptance. The provided evidence shows added enforcement, but does not establish that the prior behavior created an exploitable security vulnerability. Verification notes: The provided patch does not show the full validateHostFn body or the exact malformed host-function cases. The evidence does not prove remote exploitability, fund loss, or denial of service. The evidence does not prove an actual consensus divergence occurred before the patch. The change may also improve validation consistency between queue admission and txset validation, but the precise prior bypass is not fully demonstrated. No full validateHostFn() implementation is included in the supplied evidence. No test assertions or failure cases are shown in detail. No advisory, exploit scenario, or demonstrated consensus divergence is provided. Classification is downgraded to unclear and excluded from the security corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-validation-hardening`
Final impact type: `invalid-transaction-rejection`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, transaction-validation, soroban, hardening`

The supplied patch evidence shows new host-function validation being enforced in Soroban transaction admission, fee-bump wrapper validation, and transaction-set validity paths. In a blockchain consensus implementation, rejecting transactions as txSOROBAN_INVALID at these boundaries is security-sensitive validation hardening. However, the evidence does not show the full invalid condition, a bypass, exploitability, denial of service, fund loss, or demonstrated consensus divergence, so this should not be treated as a confirmed security fix or consensus-safety bug.

## Security Evidence

1. TransactionQueue::canAdd now rejects transactions when tx->validateHostFn() fails with txSOROBAN_INVALID.
2. FeeBumpTransactionFrame::validateHostFn() delegates validation to the inner transaction, preserving validation through the wrapper.
3. TxSetPhaseFrame::checkValid now checks TxSetUtils::getInvalidTxList(...) and requires no invalid transactions.
4. The touched paths are transaction admission and transaction-set validation in blockchain consensus code.

## Missing Evidence

1. Full validateHostFn() implementation and exact rejected host-function cases are not shown.
2. No advisory, CVE, exploit scenario, or attack precondition is provided.
3. No evidence demonstrates prior consensus divergence, denial of service, fund loss, or remote exploitability.
4. Test assertions are referenced by file list but not shown in the supplied evidence.

## Claim Boundaries

1. Keep as security hardening, not as a confirmed vulnerability fix.
2. Do not claim proven consensus failure or consensus split.
3. Do not claim fund loss, denial of service, or exploitability from the supplied patch alone.
4. Conservative impact is improved invalid Soroban transaction rejection at validation boundaries.
