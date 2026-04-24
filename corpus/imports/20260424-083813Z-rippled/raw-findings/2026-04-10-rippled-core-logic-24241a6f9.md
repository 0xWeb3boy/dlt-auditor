---
case_id: case_20260410_24241a6f9
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: high
date: 2026-04-10
source_refs:
  - git:24241a6f90f56dcb3b596fe3d21e410df9a4a387
  - "src/libxrpl/tx/transactors/check/CheckCreate.cpp:95"
  - "src/libxrpl/tx/transactors/check/CheckCreate.cpp:137"
  - "src/libxrpl/tx/invariants/MPTInvariant.cpp:593"
  - "src/libxrpl/tx/transactors/dex/OfferCreate.cpp:286"
bug_class: asset-restriction-enforcement
impact_type:
  - policy-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-validation
  - mpt
  - asset-restrictions
  - freeze-lock-checks
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a likely security fix for incomplete MPT and issued-asset restriction checks in specific CheckCreate and OfferCreate paths. The evidence shows new enforcement of TER-returning global freeze/lock checks, MPT canTransfer checks during check creation, and frozen-state checks after WeakAuth in offer acceptance. The invariant changes support detection of actual MPT balance movement, but the provided evidence does not prove theft, unauthorized minting, consensus divergence, or broad bypassability across all DEX, AMM, or Check paths.

## Observed Patch Facts

1. In `src/libxrpl/tx/transactors/check/CheckCreate.cpp`, the patch replaces `if (isGlobalFrozen(ctx.view, sendMax.asset()))` with `if (auto const ter = checkGlobalFrozen(ctx.view, sendMax.asset()); !isTesSuccess(ter))`.

2. In `src/libxrpl/tx/transactors/check/CheckCreate.cpp`, the patch replaces `return std::nullopt;` with `JLOG(ctx.j.warn()) << "Creating a check for locked MPT.";`.

3. In `src/libxrpl/tx/invariants/MPTInvariant.cpp`, the patch replaces `} // namespace xrpl` with `void`.

4. In `src/libxrpl/tx/transactors/dex/OfferCreate.cpp`, the patch replaces `return requireAuth(view, issue, id, AuthType::WeakAuth);` with `if (auto const ter = requireAuth(view, issue, id, AuthType::WeakAuth);`.

## Project Context

The changed code sits primarily in `src/libxrpl/tx/transactors/check`, `src/libxrpl/tx/transactors`, `src/libxrpl/tx/invariants`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/libxrpl/tx/transactors/dex/AMMWithdraw.cpp`, `src/libxrpl/tx/transactors/check/CheckCash.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/tx/transactors/dex/AMMWithdraw.cpp`, `src/libxrpl/tx/transactors/check/CheckCash.cpp`. The strongest project-level identifiers around this patch are `const`, `view`, `asset`, and `issue`.

## Before/After Behavior

Before the patch, CheckCreate used a boolean global-freeze predicate and manually mapped failures to tecLOCKED for MPT or tecFROZEN otherwise. After the patch, it calls checkGlobalFrozen and returns that helper's specific TER. Before the patch, the MPT CheckCreate branch rejected frozen source or destination accounts, then returned success for the branch when those checks passed. After the patch, it also calls canTransfer for the source and destination and returns the failure TER when transfer rules disallow the operation. Before the patch, OfferCreate returned directly after successful WeakAuth for an MPT accept asset. After the patch, it continues to checkFrozen. The MPT invariant code also adds before/after MPToken balance collection so finalize can reason about whether a transfer occurred.

# Root Cause

The evidenced root cause is incomplete composition of MPT and issued-asset restriction checks in selected transaction validation paths. Some paths checked one restriction category, such as authorization or per-account frozen state, without also applying another relevant check such as transfer-disabled state or frozen-state validation after WeakAuth.

## Walkthrough

1. CheckCreate previously checked non-native sendMax assets with isGlobalFrozen and converted the boolean result into a manually selected error code.

2. The patched CheckCreate path delegates that decision to checkGlobalFrozen and propagates the helper's TER result.

3. For MPT CheckCreate, the previous branch rejected individually frozen source or destination accounts but did not show a canTransfer check before accepting the branch.

4. The patched MPT CheckCreate branch preserves those frozen checks and adds canTransfer for the source-to-destination pair.

5. OfferCreate previously returned immediately from requireAuth for MPT accept assets, so the shown path did not proceed to a frozen-state check on success.

6. The patched OfferCreate path requires WeakAuth first, then separately enforces checkFrozen.

7. The MPT invariant change records before and after MPToken amounts by issuance and account, supporting finalize-time detection of actual MPT movement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/libxrpl/tx/transactors/check/CheckCreate.cpp | 95 | Reject CheckCreate when sendMax asset is globally frozen or locked, preserving the specific TER result. |
| src/libxrpl/tx/transactors/check/CheckCreate.cpp | 137 | Reject MPT CheckCreate when source or destination is frozen/locked and when canTransfer disallows the source-to-destination transfer. |
| src/libxrpl/tx/transactors/dex/OfferCreate.cpp | 286 | After WeakAuth for MPT accept assets, also enforce frozen-state checks before accepting the asset in an offer path. |
| src/libxrpl/tx/invariants/MPTInvariant.cpp | 593 | Track before/after MPT balances per issuance/account so invariant finalization can detect whether an MPT transfer occurred. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/tx/transactors/check/CheckCreate.cpp:95` (changes a sensitive control or state-update path)

Before
```cpp
// The currency may not be globally frozen
            AccountID const& issuerId{sendMax.getIssuer()};
            if (isGlobalFrozen(ctx.view, sendMax.asset()))
            {
                JLOG(ctx.j.warn()) << "Creating a check for frozen asset";
                return sendMax.asset().holds<MPTIssue>() ? tecLOCKED : tecFROZEN;
            }
            auto const err = sendMax.asset().visit(
```
After
```cpp
// The currency may not be globally frozen
            AccountID const& issuerId{sendMax.getIssuer()};
            if (auto const ter = checkGlobalFrozen(ctx.view, sendMax.asset()); !isTesSuccess(ter))
            {
                JLOG(ctx.j.warn()) << "Creating a check for frozen or locked asset";
                return ter;
            }
            auto const err = sendMax.asset().visit(
```

## Snippet 2

Context: `src/libxrpl/tx/transactors/check/CheckCreate.cpp:137` (changes a sensitive control or state-update path)

Before
```cpp
[&](MPTIssue const& issue) -> std::optional<TER> {
                    if (srcId != issuerId && isFrozen(ctx.view, srcId, issue))
                        return tecLOCKED;
                    if (dstId != issuerId && isFrozen(ctx.view, dstId, issue))
                        return tecLOCKED;

                    return std::nullopt;
```
After
```cpp
[&](MPTIssue const& issue) -> std::optional<TER> {
                    if (srcId != issuerId && isFrozen(ctx.view, srcId, issue))
                    {
                        JLOG(ctx.j.warn()) << "Creating a check for locked MPT.";
                        return tecLOCKED;
                    }
                    if (dstId != issuerId && isFrozen(ctx.view, dstId, issue))
                    {
```

## Snippet 3

Context: `src/libxrpl/tx/invariants/MPTInvariant.cpp:593` (changes a consensus- or validator-sensitive branch)

Before
```cpp
}

}  // namespace xrpl
```
After
```cpp
}

void
ValidMPTTransfer::visitEntry(
    bool,
    std::shared_ptr<SLE const> const& before,
    std::shared_ptr<SLE const> const& after)
{
```

## Snippet 4

Context: `src/libxrpl/tx/transactors/dex/OfferCreate.cpp:286` (changes a sensitive control or state-update path)

Before
```cpp
// WeakAuth - don't check if MPToken exists since it's created
            // if needed.
            return requireAuth(view, issue, id, AuthType::WeakAuth);
        });
}
```
After
```cpp
// WeakAuth - don't check if MPToken exists since it's created
            // if needed.
            if (auto const ter = requireAuth(view, issue, id, AuthType::WeakAuth);
                !isTesSuccess(ter))
            {
                return ter;
            }
```

# Fix Pattern

Compose all relevant asset restriction checks at each transaction entry point and propagate the precise TER from shared helpers rather than treating authorization, freeze, lock, and transfer-disabled checks as interchangeable.

## How It Was Fixed

CheckCreate now uses checkGlobalFrozen, adds canTransfer enforcement for MPT source-to-destination check creation, and returns the specific failure TER. OfferCreate now performs checkFrozen after successful WeakAuth for MPT accept assets. MPTInvariant now records before/after MPToken balances so finalize can identify actual MPT transfers.

# Why It Matters

1. Issuer-controlled MPT restrictions can be bypassed if transaction paths enforce only part of the required policy.

2. The shown CheckCreate path now rejects MPT checks when canTransfer disallows the source-to-destination operation.

3. The shown OfferCreate path now does not rely on WeakAuth alone for MPT accept assets.

4. The invariant update improves enforcement support, but is not by itself evidence of an exploitable bug.

# Evidence Notes

Grounded evidence is limited to the provided hunks from commit 24241a6f90f56dcb3b596fe3d21e410df9a4a387. Strong evidence exists for added checks in src/libxrpl/tx/transactors/check/CheckCreate.cpp and src/libxrpl/tx/transactors/dex/OfferCreate.cpp. The MPTInvariant.cpp hunk supports transfer-detection logic but does not establish the root cause by itself. The evidence does not establish practical exploitability, loss of funds, unauthorized minting or burning, or that all related DEX, AMM, CheckCreate, or CheckCash paths were previously bypassable. Protocol security invariant: MPT and issued-asset transaction validation should reject operations when issuer-controlled restrictions prohibit the asset use, including global freeze or lock, per-account freeze or lock, authorization requirements, and transfer-disabled rules for the relevant source and destination. Verification notes: Does not prove theft of funds or unauthorized minting/burning. Does not prove a remotely exploitable vulnerability by itself. Does not prove consensus divergence, only that consensus-relevant validation/invariant logic changed. Does not establish impact for non-MPT assets beyond the shown issued-asset freeze handling. Does not prove all DEX, AMM, or Check paths were previously bypassable; only the shown entry points are evidenced. Classified as likely rather than confirmed because only snippets and mapper context are provided. Confidence downgraded to medium because impact and exploitability are not demonstrated. Kept in the security corpus because the added checks directly enforce asset restriction policy in transaction validation paths. Helper and invariant changes are treated as supporting evidence, not the sole vulnerability cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `asset-restriction-enforcement`
Final impact type: `policy-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-validation, mpt, asset-restrictions, freeze-lock-checks`

The supplied hunks show transaction-validation paths gaining additional enforcement for frozen, locked, authorization, and transfer-disabled MPT or issued-asset states. That is security-relevant hardening of asset restriction policy in consensus-sensitive code, but the evidence does not prove a concrete exploitable vulnerability, privilege misuse, fund loss, or consensus divergence. The finding should be kept, but as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. CheckCreate now propagates checkGlobalFrozen TER results instead of using a simpler boolean frozen check.
2. CheckCreate MPT handling adds canTransfer enforcement after per-account frozen checks.
3. OfferCreate MPT accept-asset handling now continues from WeakAuth to a frozen-state check instead of returning immediately.
4. MPT invariant logic adds before/after MPToken balance tracking to reason about actual transfers.

## Missing Evidence

1. No advisory, issue text, or commit body explicitly states a security vulnerability.
2. No proof that the prior behavior enabled theft, unauthorized minting or burning, or unauthorized asset movement.
3. No regression test details are supplied showing a rejected exploit case.
4. No evidence that the invariant change fixed consensus divergence rather than improving validation coverage.

## Claim Boundaries

1. Supports only MPT and issued-asset restriction enforcement in the shown paths.
2. Does not establish broad DEX, AMM, CheckCash, or all-path bypassability.
3. Does not prove practical exploitability or attacker-controlled impact.
4. Best classified as policy-enforcement hardening, not a confirmed access-control vulnerability.
