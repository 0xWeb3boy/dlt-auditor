---
case_id: case_20260421_5ad05918f
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-21
source_refs:
  - git:5ad05918f1fcf02d0a8e6731d3db9ffb28230327
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1932"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1964"
  - "src/xrpld/app/tx/detail/InvariantCheck.h:668"
  - "src/xrpld/app/misc/PermissionedDEXHelpers.cpp:74"
bug_class: insufficient-structural-validation
impact_type:
  - protocol-invariant-enforcement
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - permissioned-dex
  - hybrid-offer
  - invariant-check
  - structural-validation
  - amendment-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a validation gap for Permissioned DEX hybrid offers: the old invariant rejected missing sfAdditionalBooks and arrays larger than one, but did not reject an empty sfAdditionalBooks array when the field was present. The evidence supports a protocol-shape validation fix, but does not establish an exploitable vulnerability or concrete security impact.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `// if a hybrid offer is missing domain or additional book, there's` with `if (after->isFlag(lsfHybrid))`.

2. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `if (txType == ttOFFER_CREATE && badHybrids_)` with `bool const isMalformed =`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.h`, the patch replaces `bool badHybrids_ = false;` with `bool badHybridsOld_ =`.

4. In `src/xrpld/app/misc/PermissionedDEXHelpers.cpp`, the patch replaces `!sleOffer->isFieldPresent(sfAdditionalBooks))` with `if (view.rules().enabled(fixSecurity3_1_3))`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/xrpld/app/misc`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/CreateOffer.cpp`, `src/xrpld/app/tx/detail/XChainBridge.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/CreateOffer.cpp`, `src/xrpld/app/tx/detail/XChainBridge.cpp`. The strongest project-level identifiers around this patch are `after`, `sfAdditionalBooks`, `isFieldPresent`, and `fixSecurity3_1_3`.

## Before/After Behavior

Before the patch, ValidPermissionedDEX::visitEntry marked a hybrid offer malformed if sfDomainID was missing, sfAdditionalBooks was missing, or sfAdditionalBooks.size() was greater than one. A present empty sfAdditionalBooks array was not covered by that predicate. After the patch, the code keeps a legacy badHybridsOld_ flag and adds a stricter post-fix badHybrids_ path that requires sfAdditionalBooks to be present with exactly one entry when fixSecurity3_1_3 is enabled. offerInDomain is updated consistently for the post-fix rule.

# Root Cause

The old malformed-hybrid-offer predicate checked for missing sfAdditionalBooks and oversized arrays, but did not encode the exact cardinality requirement. That allowed the present-but-empty case to avoid being classified as malformed in the shown invariant path.

## Walkthrough

1. Invariant scanning visits ltOFFER ledger entries and identifies hybrid offers.

2. Before the change, malformed hybrid offers were detected when sfDomainID was missing, sfAdditionalBooks was missing, or sfAdditionalBooks.size() > 1.

3. Because the predicate only rejected size greater than one, sfAdditionalBooks present with size 0 was not flagged by that condition.

4. The patch introduces separate legacy and post-fix malformed flags.

5. The post-fix path treats a hybrid offer as malformed unless sfAdditionalBooks is present and has exactly one entry.

6. finalize selects the legacy or stricter flag based on fixSecurity3_1_3.

7. PermissionedDEXHelpers::offerInDomain applies the same post-fix singleton-array requirement when checking hybrid offer domain membership.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1932 | Detects malformed ltOFFER entries during invariant scanning; changed to distinguish old and new hybrid offer validation and catch empty sfAdditionalBooks post-amendment. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1964 | Finalizes OfferCreate invariant enforcement and selects old versus fixed malformed-hybrid logic based on fixSecurity3_1_3. |
| src/xrpld/app/tx/detail/InvariantCheck.h | 668 | Stores separate pre- and post-fix malformed hybrid flags, documenting that the new rule also rejects size == 0. |
| src/xrpld/app/misc/PermissionedDEXHelpers.cpp | 74 | Checks offer domain membership and applies the post-fix rule that hybrid offers must have exactly one sfAdditionalBooks entry. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1932` (updates aggregate accounting or lifecycle state)

Before
```cpp
regularOffers_ = true;

        // if a hybrid offer is missing domain or additional book, there's
        // something wrong
        if (after->isFlag(lsfHybrid) &&
            (!after->isFieldPresent(sfDomainID) ||
             !after->isFieldPresent(sfAdditionalBooks) ||
             after->getFieldArray(sfAdditionalBooks).size() > 1))
```
After
```cpp
regularOffers_ = true;

        if (after->isFlag(lsfHybrid))
        {
            bool const hasDomainID = after->isFieldPresent(sfDomainID);
            std::optional<std::size_t> additionalBooksSize;
            if (after->isFieldPresent(sfAdditionalBooks))
                additionalBooksSize =
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1964` (updates aggregate accounting or lifecycle state)

Before
```cpp
// For each offercreate transaction, check if
    // permissioned offers are valid
    if (txType == ttOFFER_CREATE && badHybrids_)
    {
        JLOG(j.fatal()) << "Invariant failed: hybrid offer is malformed";
```
After
```cpp
// For each offercreate transaction, check if
    // permissioned offers are valid
    bool const isMalformed =
        view.rules().enabled(fixSecurity3_1_3) ? badHybrids_ : badHybridsOld_;
    if (txType == ttOFFER_CREATE && isMalformed)
    {
        JLOG(j.fatal()) << "Invariant failed: hybrid offer is malformed";
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/InvariantCheck.h:668` (updates aggregate accounting or lifecycle state)

Before
```c
{
    bool regularOffers_ = false;
    bool badHybrids_ = false;
    hash_set<uint256> domains_;
```
After
```c
{
    bool regularOffers_ = false;
    bool badHybridsOld_ =
        false;  // pre-fixSecurity3_1_3: missing field/domain or size > 1
    bool badHybrids_ =
        false;  // post-fixSecurity3_1_3: also catches size == 0 (size != 1)
    hash_set<uint256> domains_;
```

## Snippet 4

Context: `src/xrpld/app/misc/PermissionedDEXHelpers.cpp:74` (updates aggregate accounting or lifecycle state)

Before
```cpp
return false;  // LCOV_EXCL_LINE

    if (sleOffer->isFlag(lsfHybrid) &&
        !sleOffer->isFieldPresent(sfAdditionalBooks))
    {
        JLOG(j.error()) << "Hybrid offer " << offerID
                        << " missing AdditionalBooks field";
        return false;  // LCOV_EXCL_LINE
```
After
```cpp
return false;  // LCOV_EXCL_LINE

    if (view.rules().enabled(fixSecurity3_1_3))
    {
        // post-fixSecurity3_1_3: a valid hybrid offer must have
        // sfAdditionalBooks present with exactly 1 entry
        if (sleOffer->isFlag(lsfHybrid) &&
            (!sleOffer->isFieldPresent(sfAdditionalBooks) ||
```

# Fix Pattern

Replace a partial structural validation predicate with an exact cardinality check, gated by the protocol amendment so legacy and post-fix behavior remain distinct.

## How It Was Fixed

The implementation adds badHybridsOld_ for the pre-fix rule and uses badHybrids_ for the stricter post-fixSecurity3_1_3 rule. finalize chooses between them based on view.rules().enabled(fixSecurity3_1_3). PermissionedDEXHelpers::offerInDomain also rejects post-fix hybrid offers with missing or non-singleton sfAdditionalBooks.

# Why It Matters

1. Preserves the intended hybrid offer shape invariant.

2. Rejects present-but-empty sfAdditionalBooks arrays after the amendment.

3. Keeps legacy and post-amendment behavior explicitly separated.

4. Aligns invariant checking and helper-path validation.

5. Provided evidence does not prove theft, fund loss, unauthorized trading, or a consensus split.

# Evidence Notes

Grounded evidence comes from InvariantCheck.cpp, InvariantCheck.h, and PermissionedDEXHelpers.cpp. The evidence supports a malformed-offer validation gap and an amendment-gated fix. It does not show the creation path for such an offer, whether malformed offers could reach the ledger in practice, or a concrete attacker impact. The stronger draft claim of a confirmed security fix is therefore not fully supported by the supplied evidence alone. Protocol security invariant: Permissioned DEX hybrid offers are expected to have a domain binding and an sfAdditionalBooks array with exactly one entry. The patch makes the post-fixSecurity3_1_3 validation reject a present-but-empty sfAdditionalBooks array, while preserving the legacy predicate before the amendment is enabled. Verification notes: The patch evidence does not prove theft, unauthorized trading, or fund loss. The patch evidence does not show a concrete consensus split scenario. The patch evidence does not show how an empty sfAdditionalBooks hybrid offer could be created, only that validation failed to reject it in these paths. The change should not be generalized to all offer accounting or state-drift bugs; it is specifically about malformed Permissioned DEX hybrid offer shape. Confirmed by diff evidence that size == 0 was not rejected by the old size() > 1 condition. Confirmed by diff evidence that the new post-fix rule uses size != 1 semantics. Confirmed by diff evidence that behavior is gated on fixSecurity3_1_3. No supplied evidence demonstrates exploitability or direct security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-structural-validation`
Final impact type: `protocol-invariant-enforcement`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, permissioned-dex, hybrid-offer, invariant-check, structural-validation, amendment-gated`

The supplied patch evidence supports retaining this as security hardening, not a proven exploitable security fix. The change tightens validation of Permissioned DEX hybrid offers in transaction/invariant paths by requiring sfAdditionalBooks to be present with exactly one entry after fixSecurity3_1_3, closing the present-but-empty array case. However, the evidence does not show exploitability, attacker control, fund loss, unauthorized trading, or a consensus failure scenario, so the original accounting/economic impact framing is too specific.

## Security Evidence

1. Post-fix logic rejects hybrid offers unless sfAdditionalBooks is present with exactly one entry.
2. The old predicate rejected missing sfAdditionalBooks and size greater than one, but not a present empty array.
3. The invariant finalization path enforces the stricter rule for successful OfferCreate transactions when fixSecurity3_1_3 is enabled.
4. PermissionedDEXHelpers::offerInDomain is updated to apply the same stricter hybrid-offer shape requirement.
5. The code is in transaction-processing and Permissioned DEX invariant/helper paths, which are security-sensitive in a blockchain core.

## Missing Evidence

1. No evidence shows how an empty sfAdditionalBooks hybrid offer could be created or accepted into the ledger.
2. No evidence demonstrates theft, fund loss, unauthorized trading, or economic distortion.
3. No evidence demonstrates a concrete consensus split or denial-of-service scenario.
4. No test details are supplied showing the externally observable failure mode.

## Claim Boundaries

1. Validate this as amendment-gated security hardening of hybrid-offer structural rules.
2. Do not claim a confirmed exploitable vulnerability from the supplied patch alone.
3. Do not generalize the issue to all offer accounting or state drift.
4. Do not claim economic impact beyond protocol invariant enforcement without additional evidence.
