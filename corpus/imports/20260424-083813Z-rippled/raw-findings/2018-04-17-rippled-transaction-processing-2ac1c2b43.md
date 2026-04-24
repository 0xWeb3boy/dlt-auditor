---
case_id: case_20180417_2ac1c2b43
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2018-04-17
source_refs:
  - git:2ac1c2b433b8825b9a6f203f1ee65a126e20620c
  - "src/ripple/app/tx/impl/Transactor.cpp:318"
  - "src/ripple/app/tx/impl/ApplyContext.cpp:71"
  - "src/ripple/app/tx/impl/ApplyContext.h:102"
  - "src/ripple/app/tx/impl/InvariantCheck.cpp:123"
bug_class: fee-accounting-invariant
impact_type:
  - fee-overcharge-prevention
  - ledger-integrity
tags:
  - blockchain-core
  - transaction-processing
  - invariant-checking
  - fee-accounting
  - ledger-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as security hardening for rippled's transaction fee and XRP supply invariant checks. The supported claim is that invariant checking was strengthened to use the actual charged fee rather than only the fee declared in the transaction. The evidence does not establish an exploitable vulnerability, an access-control flaw, or proven XRP creation.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/Transactor.cpp`, the patch replaces `auto terResult = payFee ();` with `auto result = payFee ();`.

2. In `src/ripple/app/tx/impl/ApplyContext.cpp`, the patch replaces `template<std::size_t... Is>` with `ApplyContext::failInvariantCheck (TER const result)`.

3. In `src/ripple/app/tx/impl/ApplyContext.h`, the patch replaces `TER` with `/** Applies all invariant checkers one by one.`.

4. In `src/ripple/app/tx/impl/InvariantCheck.cpp`, the patch replaces `XRPNotCreated::finalize(STTx const& tx, TER /*tec*/, beast::Journal const& j)` with `XRPNotCreated::finalize(`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/app/tx/impl/applySteps.cpp`, `src/ripple/app/tx/impl/apply.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/applySteps.cpp`, `src/ripple/app/tx/impl/apply.cpp`. The strongest project-level identifiers around this patch are `result`, `const`, `XRPNotCreated::finalize`, and `beast::Journal`.

## Before/After Behavior

Before the change, `XRPNotCreated::finalize` derived the fee bound from `tx.getFieldAmount(sfFee)`, i.e. the transaction-declared fee. After the change, invariant finalization receives an explicit `XRPAmount const fee`, documented by `ApplyContext` as the fee charged for the transaction. The patch also centralizes invariant failure result handling in `ApplyContext::failInvariantCheck`.

# Root Cause

The supported root cause is an accounting-check mismatch: invariant code used the transaction-declared fee as its bound even though the commit states that transaction application may charge less in some insufficient-funds corner cases. That could make invariant checking less precise for runtime ledger mutations.

## Walkthrough

1. `Transactor::apply` continues to call `payFee()` and return early when fee payment fails before updating the source account state.

2. `ApplyContext` extends invariant checking to accept both the transaction result and the charged fee.

3. `XRPNotCreated::finalize` changes from reading `sfFee` from the transaction to receiving the fee as a parameter.

4. This lets the XRP delta check use the runtime charged fee rather than assuming the declared fee equals the amount destroyed.

5. `ApplyContext::failInvariantCheck` centralizes conversion of invariant failures to `tecINVARIANT_FAILED` or `tefINVARIANT_FAILED`.

6. The commit message ties the work to stronger invariant checking around not charging more than the transaction specifies and detecting anomalous conditions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/InvariantCheck.cpp | 123 | XRP supply invariant finalization now evaluates against the actual charged transaction fee rather than only the transaction-declared fee. |
| src/ripple/app/tx/impl/ApplyContext.h | 102 | Invariant-checking API is extended to accept both transaction result and charged fee. |
| src/ripple/app/tx/impl/ApplyContext.cpp | 71 | Invariant-check failure handling distinguishes failures that can still be included from fatal invariant failures that must not enter a ledger. |
| src/ripple/app/tx/impl/Transactor.cpp | 318 | Transaction apply path pays the fee before updating the source account state and participates in the invariant-checking flow. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/Transactor.cpp:318` (changes a sensitive control or state-update path)

Before
```cpp
setSeq();

        auto terResult = payFee ();

        if (terResult != tesSUCCESS) return terResult;

        view().update (sle);
```
After
```cpp
setSeq();

        auto result = payFee ();

        if (result  != tesSUCCESS)
            return result;

        view().update (sle);
```

## Snippet 2

Context: `src/ripple/app/tx/impl/ApplyContext.cpp:71` (changes a sensitive control or state-update path)

Before
```cpp
}

template<std::size_t... Is>
TER
ApplyContext::checkInvariantsHelper(TER terResult, std::index_sequence<Is...>)
{
    if (view_->rules().enabled(featureEnforceInvariants))
```
After
```cpp
}

TER
ApplyContext::failInvariantCheck (TER const result)
{
    // If we already failed invariant checks before and we are now attempting to
    // only charge a fee, and even that fails the invariant checks something is
    // very wrong. We switch to tefINVARIANT_FAILED, which does NOT get included
```

## Snippet 3

Context: `src/ripple/app/tx/impl/ApplyContext.h:102` (changes a sensitive control or state-update path)

Before
```c
}

    TER
    checkInvariants(TER);

private:
    template<std::size_t... Is>
    TER checkInvariantsHelper(TER terResult, std::index_sequence<Is...>);
```
After
```c
}

    /** Applies all invariant checkers one by one.

        @param result the result generated by processing this transaction.
        @param fee the fee charged for this transaction
        @return the result code that should be returned for this transaction.
     */
```

## Snippet 4

Context: `src/ripple/app/tx/impl/InvariantCheck.cpp:123` (changes a consensus- or validator-sensitive branch)

Before
```cpp
bool
XRPNotCreated::finalize(STTx const& tx, TER /*tec*/, beast::Journal const& j)
{
    auto fee = tx.getFieldAmount(sfFee).xrp().drops();
    if(-1*fee <= drops_ && drops_ <= 0)
        return true;
```
After
```cpp
bool
XRPNotCreated::finalize(
    STTx const& tx,
    TER const,
    XRPAmount const fee,
    beast::Journal const& j)
{
```

# Fix Pattern

Thread authoritative runtime accounting values into invariant checks instead of recomputing bounds from transaction intent fields.

## How It Was Fixed

The invariant-checking API was extended to carry the charged fee, `XRPNotCreated::finalize` was updated to use that value, and invariant failure handling was factored into a dedicated helper.

# Why It Matters

1. Improves precision of monetary accounting checks.

2. Covers cases where the charged fee differs from the declared fee.

3. Helps detect anomalous XRP destruction during transaction application.

4. Does not prove a previously exploitable attack path.

# Evidence Notes

The access-control framing from the heuristic baseline is unsupported. The strongest evidence is `InvariantCheck.cpp`, where `XRPNotCreated::finalize` stops deriving the fee from `sfFee` and instead accepts `XRPAmount const fee`; `ApplyContext.h`, where the fee is documented as the charged fee; and the commit message describing a new invariant checker for fee overcharge conditions. The provided snippets do not prove that an attacker could overcharge fees, create XRP, bypass authorization, or get an invalid ledger accepted. Protocol security invariant: Transaction application should not destroy more XRP as fees than the amount actually charged, and fee-related invariant checks should distinguish the transaction-declared fee from the runtime fee charged in corner cases where less may be collected. Verification notes: The patch does not prove that users could previously force an overcharge in a finalized ledger. The patch does not show an authorization or access-control defect. The patch does not prove XRP creation; the shown invariant primarily concerns fee destruction bounds and anomaly detection. The evidence supports protocol hardening more strongly than a confirmed exploitable vulnerability. Classified as security hardening, not a confirmed vulnerability fix. Confidence downgraded from high to medium because the provided diff excerpts do not show the full new checker or an exploit scenario. Kept in security corpus because the patch enforces a protocol monetary-accounting invariant. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fee-accounting-invariant`
Final impact type: `fee-overcharge-prevention, ledger-integrity`
Final tags: `blockchain-core, transaction-processing, invariant-checking, fee-accounting, ledger-integrity`

The supplied evidence supports retaining this as security hardening, not a confirmed exploitable vulnerability. The commit explicitly adds invariant checking to ensure fees charged do not exceed the transaction-specified fee, and the patch threads the actual charged fee into XRP supply invariant checks instead of relying on the declared transaction fee. The original access-control and privilege-misuse framing is unsupported and should be replaced with conservative fee-accounting and ledger-integrity metadata.

## Security Evidence

1. Commit message states a new invariant checker verifies fees are never higher than specified in the transaction.
2. ApplyContext API now documents and passes the actual charged fee into invariant checking.
3. XRPNotCreated::finalize changes from deriving fee from sfFee to receiving XRPAmount const fee, aligning invariant checks with runtime accounting.
4. Invariant failure handling can return tefINVARIANT_FAILED for conditions that must not be included in a ledger.

## Missing Evidence

1. No exploit path or attacker-controlled scenario is shown.
2. No evidence proves users could previously force overcharging in an accepted ledger.
3. No evidence supports an access-control or authorization bypass classification.
4. The provided snippets do not show the full new invariant checker or regression tests.

## Claim Boundaries

1. Classify as protocol security hardening around transaction fee accounting and invariant enforcement.
2. Do not claim confirmed XRP creation, theft, or privilege misuse.
3. Do not claim a concrete consensus failure beyond strengthened invariant handling.
4. Supported impact is prevention or detection of anomalous fee/XRP accounting, not a proven vulnerability exploit.
