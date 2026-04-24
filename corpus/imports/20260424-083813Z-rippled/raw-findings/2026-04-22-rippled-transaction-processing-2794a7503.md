---
case_id: case_20260422_2794a7503
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2026-04-22
source_refs:
  - git:2794a7503fee7a0d99950548af286a4e1f40e786
  - "src/libxrpl/protocol/Rules.cpp:176"
  - "include/xrpl/protocol/Rules.h:29"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:697"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:742"
bug_class: invariant-check-state-overwrite
impact_type:
  - invariant-detection-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - invariant-checking
  - security-hardening
  - feature-gated-fix
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes invariant detectors that previously overwrote stored boolean violation state for each visited ledger entry. With the fix enabled, the detectors OR-accumulate each entry's result so a previously observed violation remains recorded through the traversal. The evidence supports a security-relevant invariant-checking fix, but not a specific exploit path, funds-loss scenario, authorization bypass, or consensus-divergence claim.

## Observed Patch Facts

1. In `src/libxrpl/protocol/Rules.cpp`, the patch replaces `isFeatureEnabled(uint256 const& feature)` with `isFeatureEnabled(uint256 const& feature, bool resultIfNoRules)`.

2. In `include/xrpl/protocol/Rules.h`, the patch replaces `bool` with `/** Check whether a feature is enabled in the current ledger rules`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `xrpTrustLine_ =` with `bool const isXrp =`.

4. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `deepFreezeWithoutFreeze_ =` with `bool const bad =`.

## Project Context

The changed code sits primarily in `src/libxrpl/protocol`, `src/libxrpl`, `include/xrpl/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/libxrpl/protocol/Feature.cpp`, `src/libxrpl/protocol/STAmount.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/protocol/STAmount.cpp`, `src/xrpld/app/tx/detail/applySteps.cpp`. The strongest project-level identifiers around this patch are `feature`, `const`, `rules`, and `isFeatureEnabled`. Nearby tests or test-like files include `include/xrpl/beast/unit_test/detail/const_container.h`, `include/xrpl/beast/unit_test/suite.h`.

## Before/After Behavior

Before the patch, `NoXRPTrustLines::visitEntry` and `NoDeepFreezeTrustLinesWithoutFreeze::visitEntry` assigned their stored booleans from the current entry's predicate, so a later clean entry could replace an earlier true violation state with false. After the patch, each detector computes the current predicate into a local boolean and, when `fixSecurity3_1_3` is enabled, ORs it into the stored state. The feature helper also gains an overload that lets callers choose the default result when no current transaction rules are available, while preserving the old one-argument false-default behavior.

# Root Cause

The invariant detectors used per-entry assignment for state that needed to be latched across a full traversal. That allowed detection state from an earlier bad entry to be overwritten by a later non-bad entry.

## Walkthrough

1. Invariant checking visits ledger entries and records whether prohibited states are observed.

2. The old XRP trust-line check assigned `xrpTrustLine_` from the current entry only.

3. The old deep-freeze check assigned `deepFreezeWithoutFreeze_` from the current entry only.

4. Those assignments could clear a previously recorded true result if a later visited entry did not satisfy the violation predicate.

5. The patch computes per-entry booleans, then uses `|=` under `fixSecurity3_1_3` so earlier true results remain true.

6. The new `isFeatureEnabled(feature, resultIfNoRules)` overload supports using the fixed behavior when no transaction-rule context is available.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 697 | Accumulates detection of XRP trust-line invariant violations instead of overwriting prior true state. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 742 | Accumulates detection of deep-freeze-without-freeze invariant violations instead of overwriting prior true state. |
| src/libxrpl/protocol/Rules.cpp | 176 | Adds feature-check helper with caller-selected default when no transaction rules are available. |
| include/xrpl/protocol/Rules.h | 29 | Exposes the feature-check overload used by invariant code. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/protocol/Rules.cpp:176` (changes a sensitive control or state-update path)

Before
```cpp
bool
isFeatureEnabled(uint256 const& feature)
{
    auto const& rules = getCurrentTransactionRules();
    return rules && rules->enabled(feature);
}
```
After
```cpp
bool
isFeatureEnabled(uint256 const& feature, bool resultIfNoRules)
{
    auto const& rules = getCurrentTransactionRules();
    if (!rules)
        return resultIfNoRules;
    return rules->enabled(feature);
```

## Snippet 2

Context: `include/xrpl/protocol/Rules.h:29` (changes a sensitive control or state-update path)

Before
```c
namespace ripple {

bool
isFeatureEnabled(uint256 const& feature);
```
After
```c
namespace ripple {

/** Check whether a feature is enabled in the current ledger rules
 *
 * @param feature The feature to be tested.
 * @param resultIfNoRules What to return if called from outside a Transactor
 * context.
 */
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:697` (changes a sensitive control or state-update path)

Before
```cpp
// relying on .native() just in case native somehow
        // were systematically incorrect
        xrpTrustLine_ =
            after->getFieldAmount(sfLowLimit).issue() == xrpIssue() ||
            after->getFieldAmount(sfHighLimit).issue() == xrpIssue();
    }
}
```
After
```cpp
// relying on .native() just in case native somehow
        // were systematically incorrect
        bool const isXrp =
            after->getFieldAmount(sfLowLimit).asset() == xrpIssue() ||
            after->getFieldAmount(sfHighLimit).asset() == xrpIssue();
        if (overwriteFixEnabled)
            xrpTrustLine_ |= isXrp;
        else
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:742` (changes a sensitive control or state-update path)

Before
```cpp
bool const highDeepFreeze = uFlags & lsfHighDeepFreeze;

        deepFreezeWithoutFreeze_ =
            (lowDeepFreeze && !lowFreeze) || (highDeepFreeze && !highFreeze);
    }
}
```
After
```cpp
bool const highDeepFreeze = uFlags & lsfHighDeepFreeze;

        bool const bad =
            (lowDeepFreeze && !lowFreeze) || (highDeepFreeze && !highFreeze);
        if (overwriteFixEnabled)
            deepFreezeWithoutFreeze_ |= bad;
        else
            deepFreezeWithoutFreeze_ = bad;
```

# Fix Pattern

Latch invariant violation state across entry traversal by OR-accumulating per-entry predicates instead of overwriting stored detector state.

## How It Was Fixed

`src/xrpld/app/tx/detail/InvariantCheck.cpp` changes the XRP trust-line and deep-freeze invariant detectors to compute local booleans and OR them into the stored state when the fix feature is enabled. `src/libxrpl/protocol/Rules.cpp` and `include/xrpl/protocol/Rules.h` add a feature-check overload with a caller-selected no-rules default.

# Why It Matters

1. Invariant checks must report any violation found during traversal.

2. A later clean entry should not erase an earlier failed invariant result.

3. The affected checks guard protocol-level ledger-state invariants.

4. The evidence supports detection bypass of these invariant checks, not a proven end-to-end exploit.

# Evidence Notes

The strongest evidence is the assignment-to-OR change in `src/xrpld/app/tx/detail/InvariantCheck.cpp` for `xrpTrustLine_` and `deepFreezeWithoutFreeze_`. The Rules helper change is supporting evidence for feature-gated behavior outside a transaction-rule context. Claims about attacker capability, funds loss, authorization bypass, or consensus divergence are not established by the provided evidence. Protocol security invariant: Ledger invariant checks must preserve any violation observed during traversal; a later non-violating entry must not clear an earlier detected violation. The shown checks concern XRP trust-line detection and deep-freeze-without-freeze detection. Verification notes: The patch does not prove an attacker can create an XRP trust line. The patch does not prove an attacker can create deep-freeze-without-freeze ledger state. The patch does not show funds loss, authorization bypass, or remote exploitability. The patch does not prove consensus divergence; it only shows invariant detection could be cleared within a visit sequence. Activation depends on the `fixSecurity3_1_3` feature path shown in the code. Direct code evidence supports the boolean overwrite flaw and the OR-accumulation fix. Tests were changed in the commit, but no specific test assertions are provided in the input. Security impact is bounded to invariant-detection correctness based on the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invariant-check-state-overwrite`
Final impact type: `invariant-detection-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, invariant-checking, security-hardening, feature-gated-fix`

The patch evidence supports retaining this as security hardening, not a proven security fix. The invariant checkers previously overwrote accumulated boolean violation state while visiting ledger entries, allowing a later non-violating entry to clear an earlier detected violation. The fix latches those states with OR accumulation under a security-named feature gate. This tightens security-sensitive invariant enforcement, but the supplied evidence does not prove exploitability, funds loss, authorization bypass, or consensus divergence.

## Security Evidence

1. InvariantCheck.cpp changes violation state from assignment to OR accumulation for XRP trust-line detection.
2. InvariantCheck.cpp applies the same latching pattern to deep-freeze-without-freeze detection.
3. The affected code is an invariant-checking path in transaction processing / ledger-state validation.
4. The fix is gated through fixSecurity3_1_3 and adds a rules helper to select behavior when no transaction rules are present.

## Missing Evidence

1. No evidence that an attacker can create the prohibited ledger states.
2. No end-to-end exploit path is shown.
3. No demonstrated funds loss, authorization bypass, or remote attack impact.
4. No specific test assertions are provided in the input.
5. No proof of consensus divergence is supplied.

## Claim Boundaries

1. Treat as security hardening for invariant detection correctness, not as a confirmed exploitable vulnerability.
2. Impact is limited to possible missed invariant violations during ledger-entry traversal.
3. Do not claim funds loss, authorization bypass, or consensus failure from this evidence alone.
4. Do not rely on RPC impact; the provided patch evidence does not support that tag.
