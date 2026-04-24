---
case_id: case_20251116_248d267f2
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2025-11-16
source_refs:
  - git:248d267f21d0c4c76e4a8105a0c03fbd9b5a79f9
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2414"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:205"
  - "src/xrpld/app/tx/detail/VaultSet.cpp:145"
  - "src/xrpld/app/tx/detail/VaultClawback.cpp:72"
bug_class: numeric-validation
impact_type:
  - state-integrity
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - vault
  - numeric-validation
  - amount-validation
  - invariant-check
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a vault numeric-validation change, not an established vulnerability fix. The patch adds compatibility, validity, and representability checks in VaultCreate, VaultSet, VaultClawback, and ValidVault::finalize. It does not show an exploit path, authorization bypass, funds-at-risk scenario, or demonstrated consensus failure, and the commit context suggests baseline/build synchronization.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `auto const updatedShares = [&]() -> std::optional<Shares> {` with `if (!afterVault.assetsTotal.representable() ||`.

2. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `view().insert(vault);` with `if (asset.integral())`.

3. In `src/xrpld/app/tx/detail/VaultSet.cpp`, the patch adds `if (vault->at(sfAsset).value().integral())`.

4. In `src/xrpld/app/tx/detail/VaultClawback.cpp`, the patch replaces `if (auto const amount = ctx.tx[~sfAmount];` with `if (auto const amount = ctx.tx[~sfAmount])`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp`. The strongest project-level identifiers around this patch are `vault`, `Number::compatible`, `amount`, and `ripple::ValidVault::finalize`.

## Before/After Behavior

Before the patch, the shown VaultCreate and VaultSet snippets did not visibly validate integral-asset sfAssetsMaximum values with Number::compatible. After the patch, those paths return tecLIMIT_EXCEEDED for incompatible values. Before the patch, the shown VaultClawback preclaim rejected wrong-asset sfAmount values but did not visibly call validNumber(); after the patch it returns tecPRECISION_LOSS for invalid numeric amounts. Before the patch, the shown ValidVault::finalize excerpt moved into share update logic; after the patch it first checks several vault accounting fields with representable() and fails the invariant when they are unrepresentable.

# Root Cause

The grounded issue is missing or incomplete explicit numeric-domain checks in the visible vault paths. The supplied evidence does not establish that this caused an exploitable vulnerability or concrete security impact.

## Walkthrough

1. VaultCreate::doApply now checks integral vault sfAssetsMaximum values with valid(Number::compatible).

2. VaultSet::doApply applies the same compatibility check when sfAssetsMaximum is updated for an integral-asset vault.

3. VaultClawback::preclaim now validates optional sfAmount with validNumber() after confirming the asset matches.

4. ValidVault::finalize now checks assetsTotal, assetsAvailable, assetsMaximum, and lossUnrealized with representable().

5. If a post-apply vault field is unrepresentable, the invariant logs a fatal message, asserts, and returns according to enforcement mode.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2414 | post-apply vault invariant rejects or flags unrepresentable vault accounting fields |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 205 | vault creation rejects integral asset maximum values incompatible with protocol number limits |
| src/xrpld/app/tx/detail/VaultSet.cpp | 145 | vault update rejects integral asset maximum values incompatible with protocol number limits |
| src/xrpld/app/tx/detail/VaultClawback.cpp | 72 | clawback preclaim validates optional amount asset match and numeric validity |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:2414` (changes bounds, limits, or capacity handling)

Before
```cpp
"ripple::ValidVault::finalize : single vault operation");

    auto const updatedShares = [&]() -> std::optional<Shares> {
        // At this moment we only know that a vault is being updated and there
```
After
```cpp
"ripple::ValidVault::finalize : single vault operation");

    if (!afterVault.assetsTotal.representable() ||
        !afterVault.assetsAvailable.representable() ||
        !afterVault.assetsMaximum.representable() ||
        !afterVault.lossUnrealized.representable())
    {
        JLOG(j.fatal()) << "Invariant failed: vault overflowed maximum current "
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:205` (changes a sensitive control or state-update path)

Before
```cpp
if (scale)
        vault->at(sfScale) = scale;
    view().insert(vault);
```
After
```cpp
if (scale)
        vault->at(sfScale) = scale;
    if (asset.integral())
    {
        // Only the Maximum can be a non-zero value, so only it needs to be
        // checked.
        if (!vault->at(sfAssetsMaximum).value().valid(Number::compatible))
            return tecLIMIT_EXCEEDED;
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/VaultSet.cpp:145` (changes a sensitive control or state-update path)

Before
```cpp
return tecLIMIT_EXCEEDED;
        vault->at(sfAssetsMaximum) = tx[sfAssetsMaximum];
    }
```
After
```cpp
return tecLIMIT_EXCEEDED;
        vault->at(sfAssetsMaximum) = tx[sfAssetsMaximum];
        if (vault->at(sfAsset).value().integral())
        {
            if (!vault->at(sfAssetsMaximum).value().valid(Number::compatible))
                return tecLIMIT_EXCEEDED;
        }
    }
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/VaultClawback.cpp:72` (changes a sensitive control or state-update path)

Before
```cpp
Asset const vaultAsset = vault->at(sfAsset);
    if (auto const amount = ctx.tx[~sfAmount];
        amount && vaultAsset != amount->asset())
        return tecWRONG_ASSET;

    if (vaultAsset.native())
```
After
```cpp
Asset const vaultAsset = vault->at(sfAsset);
    if (auto const amount = ctx.tx[~sfAmount])
    {
        if (vaultAsset != amount->asset())
            return tecWRONG_ASSET;
        else if (!amount->validNumber())
            return tecPRECISION_LOSS;
```

# Fix Pattern

Add explicit numeric validity and representability checks around vault amount inputs and post-apply vault accounting state.

## How It Was Fixed

The patch rejects incompatible integral sfAssetsMaximum values during vault creation and update, rejects invalid clawback amount numbers, and adds a post-apply invariant for unrepresentable vault accounting fields.

# Why It Matters

1. Keeps vault amount fields within expected numeric limits.

2. Reduces risk of precision loss or invalid numeric state.

3. Adds invariant coverage for vault accounting fields.

4. Security impact is plausible but not proven by the provided evidence.

# Evidence Notes

Primary evidence is from InvariantCheck.cpp, VaultCreate.cpp, VaultSet.cpp, and VaultClawback.cpp. The evidence does not support the heuristic access-control claim. It also does not prove a concrete exploit path, stolen funds, authorization bypass, or consensus split. Commit subject/body indicate baseline/build-related work, which further weakens classification as a confirmed security fix. Protocol security invariant: Vault ledger amounts and limits should remain within the protocol's valid and representable numeric domain, especially for integral assets and post-apply vault accounting fields. Verification notes: No authorization or role-check weakness is proven by the patch evidence. No concrete exploit path is shown. No evidence shows funds can be stolen or access controls bypassed. The patch may be baseline synchronization or build-related cleanup with security-relevant numeric hardening. The exact runtime impact of an unrepresentable vault value is not proven beyond invariant/transaction rejection behavior. Classified as numeric validation rather than access control. Downgraded security verdict because vulnerability impact is not established. Set keep_in_security_corpus to false under the unclear-security rule. No external context or repository inspection was used. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `numeric-validation`
Final impact type: `state-integrity, consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, vault, numeric-validation, amount-validation, invariant-check`

The evidence does not support the original access-control framing or a confirmed exploitable security fix, but it does show security-relevant hardening in a blockchain transaction and invariant path. The patch adds explicit rejection of invalid, incompatible, or unrepresentable vault numeric state in VaultCreate, VaultSet, VaultClawback, and ValidVault::finalize. Given the consensus-ledger context, preventing invalid amount domains and overflow-like unrepresentable accounting state is enough to retain as security-hardening, not as a concrete security-fix.

## Security Evidence

1. VaultCreate rejects integral sfAssetsMaximum values that are not valid under Number::compatible.
2. VaultSet applies the same Number::compatible validation when updating sfAssetsMaximum.
3. VaultClawback now rejects optional sfAmount values that fail validNumber().
4. ValidVault::finalize adds invariant checks for unrepresentable vault accounting fields and fails enforcement on overflow-like state.
5. The touched code is transaction application and invariant logic for blockchain vault ledger state.

## Missing Evidence

1. No exploit path is shown.
2. No demonstrated funds loss, unauthorized action, or privilege bypass is shown.
3. No consensus split or node crash scenario is proven by the supplied patch.
4. Commit subject/body suggest baseline/build synchronization rather than an explicit security advisory.
5. No regression test evidence is supplied in the provided excerpts.

## Claim Boundaries

1. Classify as numeric validation and invariant hardening, not access control.
2. Do not claim a confirmed vulnerability or exploitable bug.
3. Do not claim privilege misuse or authorization bypass.
4. Do not claim concrete financial loss or consensus failure from the evidence alone.
5. Keep only as security-hardening due to security-sensitive ledger numeric-domain tightening.
