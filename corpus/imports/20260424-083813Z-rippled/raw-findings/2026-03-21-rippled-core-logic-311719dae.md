---
case_id: case_20260321_311719dae
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: high
date: 2026-03-21
source_refs:
  - git:311719daeb10887eca3f4b049e46013cee68fd43
  - "src/libxrpl/tx/invariants/InvariantCheck.cpp:666"
  - "src/libxrpl/tx/invariants/InvariantCheck.cpp:625"
  - "src/libxrpl/tx/invariants/InvariantCheck.cpp:359"
  - "src/libxrpl/tx/invariants/InvariantCheck.cpp:613"
bug_class: invariant-state-overwrite
impact_type:
  - ledger-integrity
  - consensus-safety
tags:
  - blockchain-core
  - consensus
  - invariant-checks
  - ledger-integrity
  - state-tracking
  - amendment-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix in rippled transaction invariant enforcement. The evidence supports a consensus-sensitive invariant bug where boolean violation state could use last-entry overwrite semantics instead of latching any observed violation. The patch adds amendment-gated selection between corrected accumulated state and legacy behavior for the three named invariant checks. The evidence does not support the draft's discarded access-control framing and does not prove a practical exploit path.

## Observed Patch Facts

1. In `src/libxrpl/tx/invariants/InvariantCheck.cpp`, the patch replaces `ReadView const&,` with `ReadView const& rv,`.

2. In `src/libxrpl/tx/invariants/InvariantCheck.cpp`, the patch replaces `ReadView const&,` with `ReadView const& rv,`.

3. In `src/libxrpl/tx/invariants/InvariantCheck.cpp`, the patch replaces `if (bad_)` with `bool const effectiveBad = rv.rules().enabled(fixInvariantOverwrite) ? bad_ : badLegacy_;`.

4. In `src/libxrpl/tx/invariants/InvariantCheck.cpp`, the patch replaces `xrpTrustLine_ |= after->getFieldAmount(sfLowLimit).issue() == xrpIssue() ||` with `bool const isXrp = after->getFieldAmount(sfLowLimit).issue() == xrpIssue() ||`.

## Project Context

The changed code sits primarily in `src/libxrpl/tx/invariants`, `src/libxrpl/tx`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/libxrpl/tx/invariants/VaultInvariant.cpp`, `src/libxrpl/tx/invariants/PermissionedDomainInvariant.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/tx/invariants/VaultInvariant.cpp`, `src/libxrpl/tx/invariants/PermissionedDomainInvariant.cpp`. The strongest project-level identifiers around this patch are `const`, `beast::Journal`, `ReadView`, and `xrpTrustLine_`.

## Before/After Behavior

Before the change, affected invariant finalizers made pass/fail decisions from tracked boolean flags that the commit body says could be overwritten across multiple visited entries. That meant an earlier bad entry could be hidden by a later good entry before finalize. After the change, finalize receives ReadView, checks whether fixInvariantOverwrite is enabled, and chooses the corrected accumulated flag or a preserved legacy flag. The shown NoXRPTrustLines visitEntry hunk computes isXrp, latches xrpTrustLine_ with |= isXrp, and stores xrpTrustLineLegacy_ = isXrp for old behavior.

# Root Cause

The supported root cause is incorrect boolean state tracking for invariant checks across multiple visited ledger entries. The invariant result should represent whether any visited entry violated the invariant, but legacy behavior could represent only the last visited entry for the affected checks.

## Walkthrough

1. An invariant check visits ledger entries and records whether it observed a prohibited state.

2. The commit body states three checks used assignment instead of accumulated boolean OR for violation tracking.

3. With overwrite semantics, a later non-violating entry could clear a violation observed earlier in the same invariant pass.

4. Finalize then could make its decision from the cleared flag and fail to report the earlier violation.

5. The patch maintains corrected accumulated state and separate legacy state.

6. Finalize selects corrected or legacy behavior based on the fixInvariantOverwrite amendment gate.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/libxrpl/tx/invariants/InvariantCheck.cpp | 359 | NoZeroEscrow finalize selects fixed accumulated bad_ versus legacy badLegacy_ under fixInvariantOverwrite before rejecting invalid escrow amount state. |
| src/libxrpl/tx/invariants/InvariantCheck.cpp | 613 | NoXRPTrustLines visitEntry now latches any XRP trust line observation in xrpTrustLine_ while preserving legacy last-entry behavior in xrpTrustLineLegacy_. |
| src/libxrpl/tx/invariants/InvariantCheck.cpp | 625 | NoXRPTrustLines finalize uses amendment-gated fixed or legacy flag to decide whether the invariant failed. |
| src/libxrpl/tx/invariants/InvariantCheck.cpp | 666 | NoDeepFreezeTrustLinesWithoutFreeze finalize uses amendment-gated fixed or legacy flag to decide whether the invariant failed. |
| include/xrpl/protocol/detail/features.macro | 0 | Defines or registers the fixInvariantOverwrite amendment gate used to preserve pre-amendment consensus behavior. |
| include/xrpl/tx/invariants/InvariantCheck.h | 0 | Declares fixed and legacy tracking state for the affected invariant classes. |
| src/test/app/Invariants_test.cpp | 0 | Adds or updates regression coverage for amendment-gated invariant overwrite behavior. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/tx/invariants/InvariantCheck.cpp:666` (changes a sensitive control or state-update path)

Before
```cpp
TER const,
    XRPAmount const,
    ReadView const&,
    beast::Journal const& j) const
{
    if (!deepFreezeWithoutFreeze_)
        return true;
```
After
```cpp
TER const,
    XRPAmount const,
    ReadView const& rv,
    beast::Journal const& j) const
{
    bool const bad = rv.rules().enabled(fixInvariantOverwrite) ? deepFreezeWithoutFreeze_
                                                               : deepFreezeWithoutFreezeLegacy_;
```

## Snippet 2

Context: `src/libxrpl/tx/invariants/InvariantCheck.cpp:625` (changes a sensitive control or state-update path)

Before
```cpp
TER const,
    XRPAmount const,
    ReadView const&,
    beast::Journal const& j) const
{
    if (!xrpTrustLine_)
        return true;
```
After
```cpp
TER const,
    XRPAmount const,
    ReadView const& rv,
    beast::Journal const& j) const
{
    bool const bad =
        rv.rules().enabled(fixInvariantOverwrite) ? xrpTrustLine_ : xrpTrustLineLegacy_;
```

## Snippet 3

Context: `src/libxrpl/tx/invariants/InvariantCheck.cpp:359` (changes a sensitive control or state-update path)

Before
```cpp
beast::Journal const& j) const
{
    if (bad_)
    {
        JLOG(j.fatal()) << "Invariant failed: escrow specifies invalid amount";
```
After
```cpp
beast::Journal const& j) const
{
    bool const effectiveBad = rv.rules().enabled(fixInvariantOverwrite) ? bad_ : badLegacy_;

    if (effectiveBad)
    {
        JLOG(j.fatal()) << "Invariant failed: escrow specifies invalid amount";
```

## Snippet 4

Context: `src/libxrpl/tx/invariants/InvariantCheck.cpp:613` (changes a sensitive control or state-update path)

Before
```cpp
// relying on .native() just in case native somehow
        // were systematically incorrect
        xrpTrustLine_ |= after->getFieldAmount(sfLowLimit).issue() == xrpIssue() ||
            after->getFieldAmount(sfHighLimit).issue() == xrpIssue();
    }
}
```
After
```cpp
// relying on .native() just in case native somehow
        // were systematically incorrect
        bool const isXrp = after->getFieldAmount(sfLowLimit).issue() == xrpIssue() ||
            after->getFieldAmount(sfHighLimit).issue() == xrpIssue();
        xrpTrustLine_ |= isXrp;
        xrpTrustLineLegacy_ = isXrp;
    }
}
```

# Fix Pattern

Latch invariant violations with boolean OR across visited entries, while preserving legacy overwrite behavior behind a consensus amendment gate.

## How It Was Fixed

The patch introduces or uses fixInvariantOverwrite and changes the affected invariant checks to keep both fixed and legacy tracking state. Corrected state accumulates violations so once a bad condition is observed it remains visible to finalize. Legacy state preserves prior overwrite behavior. Finalize methods now consult ReadView rules and choose the appropriate state before returning success or failure.

# Why It Matters

1. Invariant checks protect ledger-state validity during transaction processing.

2. A later compliant entry should not erase an earlier observed invariant violation.

3. The amendment gate indicates the behavior change is consensus-sensitive.

4. The evidence is limited to the three named invariant checks.

# Evidence Notes

Grounded evidence comes from InvariantCheck.cpp finalizers for NoZeroEscrow, NoXRPTrustLines, and NoDeepFreezeTrustLinesWithoutFreeze selecting fixed versus legacy flags under fixInvariantOverwrite, plus the NoXRPTrustLines visitEntry hunk showing accumulated fixed state and legacy assignment state. The commit body supplies the clearest statement that three invariant checks used assignment where accumulation was required. The evidence does not establish access control, privilege bypass, attacker prerequisites, exploitability through normal transaction flows, or impact beyond the three named checks. The NoXRPTrustLines before excerpt already shows |=, so that specific hunk alone does not prove the old overwrite bug; the root-cause claim depends partly on the commit message and broader mapper context. Protocol security invariant: Transaction invariant checks must preserve any violation observed while visiting ledger entries until finalize; a later compliant entry must not clear an earlier violation for the affected NoZeroEscrow, NoXRPTrustLines, and NoDeepFreezeTrustLinesWithoutFreeze checks when the corrected amendment behavior is active. Verification notes: The patch does not show an access-control or authorization bug. The evidence does not prove a practical exploit path or attacker prerequisites. The evidence does not prove that normal transaction logic can create all invalid states without the invariant layer. The legacy behavior is intentionally preserved before amendment activation for consensus compatibility. Only the three named invariant checks are shown affected by this specific overwrite bug. Downgraded from confirmed to likely because exploitability and attacker-controlled reachability are not shown. Rejected access-control classification as unsupported. Kept in security corpus because transaction invariant bypass in a consensus ledger is security-relevant when grounded to invalid state detection. No independent file inspection or external context was used. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invariant-state-overwrite`
Final impact type: `ledger-integrity, consensus-safety`
Final tags: `blockchain-core, consensus, invariant-checks, ledger-integrity, state-tracking, amendment-gated`

The evidence supports retaining this as security hardening rather than a fully proven security fix. The patch corrects boolean violation tracking in consensus-sensitive transaction invariant checks so earlier bad ledger entries cannot be hidden by later good entries, while preserving legacy behavior behind an amendment gate. That is security-relevant for ledger integrity, but the supplied evidence does not prove attacker reachability, practical exploitability, or an access-control/privilege-misuse impact.

## Security Evidence

1. Commit body states invariant checks used assignment instead of accumulated OR, allowing later entries to overwrite earlier violations.
2. Affected code is in transaction invariant finalizers for NoZeroEscrow, NoXRPTrustLines, and NoDeepFreezeTrustLinesWithoutFreeze.
3. Patch selects fixed accumulated state versus legacy overwrite state using the fixInvariantOverwrite amendment gate.
4. NoXRPTrustLines evidence shows fixed state latching with |= while preserving legacy assignment behavior.

## Missing Evidence

1. No demonstrated transaction path showing an attacker can create the invalid states.
2. No proof that the bug caused consensus divergence, fund loss, authorization bypass, or privilege misuse.
3. No full before/after evidence for every affected visitEntry assignment site.
4. No evidence supporting the original access-control classification.

## Claim Boundaries

1. Classify as invariant state tracking hardening, not access control.
2. Limit scope to the three named invariant checks in the commit body and supplied hunks.
3. Do not claim a practical exploit or concrete asset loss from the supplied patch alone.
4. Do not claim behavior changes before amendment activation because legacy behavior is intentionally preserved.
