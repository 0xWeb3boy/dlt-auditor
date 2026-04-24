---
case_id: case_20180302_8d9dffcf8
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2018-03-02
source_refs:
  - git:8d9dffcf846c3737e9150acf0cf3940fcfab4aa4
  - "src/ripple/app/tx/impl/Escrow.cpp:159"
  - "src/ripple/app/tx/impl/Escrow.cpp:365"
  - "src/ripple/app/tx/impl/Escrow.cpp:110"
  - "src/ripple/app/tx/impl/Escrow.cpp:42"
bug_class: escrow-condition-validation-hardening
impact_type:
  - escrow-release-policy-hardening
  - economic-risk-reduction
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - escrow
  - consensus-rule
  - validation-hardening
  - timelock-semantics
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes XRP Ledger escrow creation and finish semantics under the fix1571 amendment. It prevents newly created CancelAfter-only escrows from being immediately finishable unless a cryptocondition is present, tightens parent-close-time checks, and adjusts EscrowFinish timing logic. The commit describes the old behavior as documented but unintuitive and confusing, so the evidence supports a consensus-rule clarification or hardening change, not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/Escrow.cpp`, the patch replaces `if (ctx_.tx[~sfCancelAfter])` with `// Prior to fix1571, the cancel and finish times could be greater`.

2. In `src/ripple/app/tx/impl/Escrow.cpp`, the patch replaces `// Too soon?` with `// If a cancel time is present, a finish operation should only succeed prior`.

3. In `src/ripple/app/tx/impl/Escrow.cpp`, the patch replaces `if (! ctx.tx[~sfCancelAfter] &&` with `// We must specify at least one timeout value`.

4. In `src/ripple/app/tx/impl/Escrow.cpp`, the patch replaces `Escrow allows an account holder to sequester any amount` with `Escrow`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/app/tx/impl/PayChan.cpp`, `src/ripple/app/tx/impl/Transactor.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/PayChan.cpp`, `src/ripple/app/tx/impl/Transactor.h`. The strongest project-level identifiers around this patch are `ctx_`, `time`, `sfFinishAfter`, and `sfCancelAfter`.

## Before/After Behavior

Before the change, EscrowCreate accepted a transaction with CancelAfter but no FinishAfter because at least one timeout field was present. The commit states such an escrow could be completed immediately with EscrowFinish. After the change, under fix1571, a new escrow without FinishAfter must include a cryptocondition. The patch also changes create-time boundary checks for CancelAfter and FinishAfter to require times strictly greater than parentCloseTime and rewrites finish-time checks around FinishAfter and CancelAfter.

# Root Cause

The pre-fix rules allowed CancelAfter to satisfy the minimum timeout requirement even though CancelAfter is a cancellation deadline, not an explicit finish requirement. That produced documented but potentially confusing escrow behavior where an escrow could be finished immediately if no FinishAfter or cryptocondition constrained release.

## Walkthrough

1. EscrowCreate::preflight validates amount and timeout fields.

2. Before fix1571, preflight rejected creation only when both sfCancelAfter and sfFinishAfter were absent.

3. A transaction with sfCancelAfter but no sfFinishAfter could therefore pass creation checks.

4. The commit states this produced an escrow that could be immediately completed using EscrowFinish.

5. Under fix1571, EscrowCreate::preflight requires either sfFinishAfter or a cryptocondition when creating this kind of escrow.

6. EscrowCreate::doApply adds fix1571-gated strict comparisons against parentCloseTime for present cancel and finish times.

7. EscrowFinish::doApply adds fix1571-gated timing logic for FinishAfter and CancelAfter handling.

8. Feature.h and Feature.cpp register the fix1571 amendment gate for consensus activation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/Escrow.cpp | 110 | EscrowCreate preflight rejects newly created escrows that would have no explicit finish requirement under fix1571. |
| src/ripple/app/tx/impl/Escrow.cpp | 159 | EscrowCreate apply enforces stricter parent-close-time comparisons for CancelAfter and FinishAfter under fix1571. |
| src/ripple/app/tx/impl/Escrow.cpp | 365 | EscrowFinish apply enforces finish timing and cancel deadline semantics for existing escrow ledger entries. |
| src/ripple/protocol/Feature.h | 0 | Declares the fix1571 amendment gate for consensus activation. |
| src/ripple/protocol/impl/Feature.cpp | 0 | Registers the fix1571 amendment feature used by escrow validation. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/Escrow.cpp:159` (updates aggregate accounting or lifecycle state)

Before
```cpp
auto const closeTime = ctx_.view ().info ().parentCloseTime;

    if (ctx_.tx[~sfCancelAfter])
    {
        auto const cancelAfter = ctx_.tx[sfCancelAfter];

        if (closeTime.time_since_epoch().count() >= cancelAfter)
            return tecNO_PERMISSION;
```
After
```cpp
auto const closeTime = ctx_.view ().info ().parentCloseTime;

    // Prior to fix1571, the cancel and finish times could be greater
    // than or equal to the parent ledgers' close time.
    //
    // With fix1571, we require that they both be strictly greater
    // than the parent ledgers' close time.
    if (ctx_.view ().rules().enabled(fix1571))
```

## Snippet 2

Context: `src/ripple/app/tx/impl/Escrow.cpp:365` (updates aggregate accounting or lifecycle state)

Before
```cpp
return tecNO_TARGET;

    // Too soon?
    if ((*slep)[~sfFinishAfter] &&
        ctx_.view().info().parentCloseTime.time_since_epoch().count() <=
            (*slep)[sfFinishAfter])
        return tecNO_PERMISSION;
```
After
```cpp
return tecNO_TARGET;

    // If a cancel time is present, a finish operation should only succeed prior
    // to that time. fix1571 corrects a logic error in the check that would make
    // a finish only succeed strictly after the cancel time.
    if (ctx_.view ().rules().enabled(fix1571))
    {
        auto const now = ctx_.view().info().parentCloseTime;
```

## Snippet 3

Context: `src/ripple/app/tx/impl/Escrow.cpp:110` (updates aggregate accounting or lifecycle state)

Before
```cpp
return temBAD_AMOUNT;

    if (! ctx.tx[~sfCancelAfter] &&
            ! ctx.tx[~sfFinishAfter])
        return temBAD_EXPIRATION;

    if (ctx.tx[~sfCancelAfter] && ctx.tx[~sfFinishAfter] &&
            ctx.tx[sfCancelAfter] <= ctx.tx[sfFinishAfter])
```
After
```cpp
return temBAD_AMOUNT;

    // We must specify at least one timeout value
    if (! ctx.tx[~sfCancelAfter] && ! ctx.tx[~sfFinishAfter])
            return temBAD_EXPIRATION;

    // If both finish and cancel times are specified then the cancel time must
    // be strictly after the finish time.
```

## Snippet 4

Context: `src/ripple/app/tx/impl/Escrow.cpp:42` (updates aggregate accounting or lifecycle state)

Before
```cpp
/*
    Escrow allows an account holder to sequester any amount
    of XRP in its own ledger entry, until the escrow process
    either finishes or is canceled.

    If the escrow process finishes successfully, then the
    destination account (which must exist) will receives the
```
After
```cpp
/*
    Escrow
    ======

    Escrow is a feature of the XRP Ledger that allows you to send conditional
    XRP payments. These conditional payments, called escrows, set aside XRP and
    deliver it later when certain conditions are met. Conditions to successfully
```

# Fix Pattern

Add an amendment-gated validation rule that rejects ambiguous escrow creation states, and align apply-time timing checks with the revised escrow semantics.

## How It Was Fixed

The patch introduces fix1571 and applies it in Escrow.cpp. Under the amendment, CancelAfter alone is no longer enough to create a new escrow unless a cryptocondition is also specified. The patch also makes present CancelAfter and FinishAfter values strictly greater than parentCloseTime at creation and updates EscrowFinish logic to handle FinishAfter and CancelAfter boundaries explicitly.

# Why It Matters

1. Prevents new escrows with no explicit finish delay or condition.

2. Reduces confusing documented behavior around CancelAfter-only escrows.

3. Changes consensus-gated transaction validation semantics.

4. Evidence does not show theft, signature bypass, cryptocondition forgery, or ledger corruption.

# Evidence Notes

Grounded evidence is limited to Escrow.cpp changes in EscrowCreate::preflight, EscrowCreate::doApply, and EscrowFinish::doApply, plus the commit message and amendment registration paths. The commit explicitly frames the old behavior as documented but unintuitive. Claims of a proven vulnerability, exploitable theft, accounting drift, ledger corruption, or cryptographic bypass are unsupported by the provided evidence. Protocol security invariant: New escrow entries should have explicit conditions that make their finish behavior clear: a FinishAfter time and/or a cryptocondition, with finish attempts evaluated against the ledger entry's timing fields. The provided evidence does not establish that the pre-fix documented behavior violated a security invariant. Verification notes: The patch does not prove theft of funds from correctly constructed escrows. The commit says the immediate-finish behavior was documented, so user confusion is shown more clearly than protocol violation before activation. No exploit path involving signature bypass, cryptocondition forgery, or ledger corruption is shown. The evidence does not prove impact on escrows created before the amendment beyond the gated finish-time behavior. Downgraded from likely security-hardening to unclear because the vulnerability thesis is not established. Set keep_in_security_corpus to false under the rule for unclear security relevance. Removed unsupported accounting/state-drift framing from the heuristic baseline. Preserved the grounded escrow timing and validation behavior described by the diff and commit message. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `escrow-condition-validation-hardening`
Final impact type: `escrow-release-policy-hardening, economic-risk-reduction`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, escrow, consensus-rule, validation-hardening, timelock-semantics`

The evidence does not prove an exploitable vulnerability, and the commit explicitly frames the old behavior as documented but unintuitive. However, the patch is amendment-gated consensus logic that tightens security-sensitive escrow creation and finish semantics: new escrows can no longer be created in a state that is immediately finishable without an explicit finish time or cryptocondition, and timing boundary checks are strengthened. This is best retained as security hardening, not a confirmed security fix.

## Security Evidence

1. EscrowCreate validation now requires a FinishAfter value or cryptocondition for cases that otherwise could be immediately finished.
2. The change is gated by fix1571, indicating a consensus-rule amendment rather than ordinary cleanup.
3. EscrowCreate apply-time checks tighten CancelAfter and FinishAfter comparisons against parentCloseTime.
4. EscrowFinish logic is revised around finish and cancel timing semantics, with comments describing a corrected logic error.

## Missing Evidence

1. No evidence of theft, unauthorized signature use, cryptocondition bypass, or ledger corruption is provided.
2. The commit says the prior immediate-finish behavior was documented, which weakens a concrete vulnerability claim.
3. No exploit scenario or affected-user loss mechanism is shown beyond confusing escrow semantics.
4. No full test evidence is supplied showing a security regression case.

## Claim Boundaries

1. Classify as hardening of escrow validation and timing semantics, not as a proven fund-theft vulnerability.
2. Do not claim accounting drift or state corruption from the supplied patch alone.
3. Do not claim impact on already-created escrows except where fix1571-gated finish behavior is directly evidenced.
4. Do not infer cryptographic failure; the patch concerns validation rules and time-based escrow conditions.
