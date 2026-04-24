---
case_id: case_20250602_7e24adbdd
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: high
source_quality: high
date: 2025-06-02
source_refs:
  - git:7e24adbdd0b61fb50967c4c6d4b27cc6d81b33f3
  - "src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:610"
  - "src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:324"
  - "src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:230"
  - "src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:161"
tags:
  - blockchain-core
  - transaction-processing
  - access-control
  - privilege-misuse
  - nft
  - trustline-authorization
  - issued-assets
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an authorization enforcement gap in `NFTokenAcceptOffer::preclaim` for non-native issued-asset NFT offer acceptance. The supplied snippets show new `fixEnforceNFTokenTrustlineV2`-gated calls to `nft::checkTrustlineAuthorized` for broker fee receipt, buy-offer acceptance where issued currency is involved, and sell-offer acceptance paths that previously used a different asset acceptance helper. The commit message directly states the issue was NFT transactions bypassing trustline authorization and a potential deep-frozen trustline invariant violation.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp`, the patch replaces `TER` with `} // namespace ripple`.

2. In `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp`, the patch replaces `// This is a similar approach taken by usual offers.` with `if (ctx.view.rules().enabled(fixEnforceNFTokenTrustlineV2))`.

3. In `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp`, the patch adds `// Check that the account accepting the buy offer (he's selling the NFT)`.

4. In `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp`, the patch adds `// Check if broker is allowed to receive the fee with these IOUs.`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/apply.cpp`, `src/xrpld/app/tx/detail/XChainBridge.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/NFTokenUtils.cpp`, `src/xrpld/app/tx/detail/apply.cpp`. The strongest project-level identifiers around this patch are `nft::checkTrustlineAuthorized`, `view`, `const`, and `rules`.

## Before/After Behavior

Before the patch, the visible `NFTokenAcceptOffer::preclaim` paths performed amount, balance, and broker-fee checks, and one non-native sell-offer path used `checkAcceptAsset`; the supplied before snippets do not show equivalent `nft::checkTrustlineAuthorized` checks for the broker fee recipient, buy-offer owner, or sell-offer non-native acceptance path. After the patch, those non-native paths are guarded by `fixEnforceNFTokenTrustlineV2` and call `nft::checkTrustlineAuthorized`, returning an error if authorization fails. The old `NFTokenAcceptOffer::checkAcceptAsset` implementation is removed from the shown file excerpt.

# Root Cause

NFT accept-offer processing did not consistently route all relevant non-native issued-asset participants through the NFT trustline authorization check. As a result, some NFT transaction paths could proceed after balance or amount validation without the trustline authorization enforcement identified by the commit message.

## Walkthrough

1. `NFTokenAcceptOffer::preclaim` validates NFT offer acceptance conditions such as amounts, balances, and broker fee constraints.

2. For brokered transactions, the patch adds a feature-gated non-native broker-fee check using `nft::checkTrustlineAuthorized` for `ctx.tx[sfAccount]`.

3. For buy-offer acceptance involving issued currency, the patch adds a feature-gated authorization check for `bo->at(sfOwner)`.

4. For sell-offer acceptance involving a non-native payment, the patch replaces the prior `checkAcceptAsset` path with a `fixEnforceNFTokenTrustlineV2`-gated call to `nft::checkTrustlineAuthorized`.

5. If any new authorization check fails, `preclaim` returns that result before the transaction can proceed.

6. The removed `checkAcceptAsset` implementation supports the conclusion that this path was being changed to use the NFT-specific trustline authorization utility.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp | 155 | Adds broker-fee recipient trustline authorization check for non-native IOU broker fees. |
| src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp | 224 | Adds authorization checks when accepting a buy offer where the NFT seller receives issued currency. |
| src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp | 318 | Replaces prior asset acceptance helper path with feature-gated NFT trustline authorization for non-native sell-offer acceptance. |
| src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp | 610 | Removes or relocates the old `checkAcceptAsset` helper path, indicating trustline validation is centralized through NFT utility authorization checks. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:610` (changes a sensitive control or state-update path)

Before
```cpp
}

TER
NFTokenAcceptOffer::checkAcceptAsset(
    ReadView const& view,
    ApplyFlags const flags,
    AccountID const id,
    beast::Journal const j,
```
After
```cpp
}

}  // namespace ripple
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:324` (changes a sensitive control or state-update path)

Before
```cpp
// Make sure that we are allowed to hold what the taker will pay us.
        // This is a similar approach taken by usual offers.
        if (!needed.native())
        {
            auto const result = checkAcceptAsset(
                ctx.view,
                ctx.flags,
```
After
```cpp
// Make sure that we are allowed to hold what the taker will pay us.
        if (!needed.native())
        {
            if (ctx.view.rules().enabled(fixEnforceNFTokenTrustlineV2))
            {
                auto res = nft::checkTrustlineAuthorized(
                    ctx.view,
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:230` (changes a sensitive control or state-update path)

Before
```cpp
ctx.j) < needed)
            return tecINSUFFICIENT_FUNDS;
    }
```
After
```cpp
ctx.j) < needed)
            return tecINSUFFICIENT_FUNDS;

        // Check that the account accepting the buy offer (he's selling the NFT)
        // is allowed to receive IOUs. Also check that this offer's creator is
        // authorized. But we need to exclude the case when the transaction is
        // created by the broker.
        if (ctx.view.rules().enabled(fixEnforceNFTokenTrustlineV2) &&
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp:161` (changes a sensitive control or state-update path)

Before
```cpp
if ((*so)[sfAmount] > (*bo)[sfAmount] - *brokerFee)
                return tecINSUFFICIENT_PAYMENT;
        }
    }
```
After
```cpp
if ((*so)[sfAmount] > (*bo)[sfAmount] - *brokerFee)
                return tecINSUFFICIENT_PAYMENT;

            // Check if broker is allowed to receive the fee with these IOUs.
            if (!brokerFee->native() &&
                ctx.view.rules().enabled(fixEnforceNFTokenTrustlineV2))
            {
                auto res = nft::checkTrustlineAuthorized(
```

# Fix Pattern

Add explicit, feature-gated trustline authorization checks in preclaim for non-native issued-asset NFT offer acceptance paths before continuing transaction processing.

## How It Was Fixed

The implementation adds `ctx.view.rules().enabled(fixEnforceNFTokenTrustlineV2)` checks around calls to `nft::checkTrustlineAuthorized` in the relevant non-native IOU paths of `NFTokenAcceptOffer::preclaim`, and removes the old local `checkAcceptAsset` helper implementation from `NFTokenAcceptOffer.cpp`.

# Why It Matters

1. Prevents NFT offer acceptance from bypassing required IOU trustline authorization.

2. Covers broker-fee receipt as a distinct non-native asset recipient path.

3. Aligns NFT offer acceptance with the trustline authorization invariant stated in the commit message.

4. Evidence does not establish arbitrary ledger writes, theft, or a proven consensus failure.

# Evidence Notes

Primary evidence is from `src/xrpld/app/tx/detail/NFTokenAcceptOffer.cpp` at the supplied line contexts around 155, 224, 318, and 610. The strongest support is the combination of new `nft::checkTrustlineAuthorized` calls in preclaim and the commit body explicitly describing NFT transactions bypassing trustline authorization. Deep-freeze relevance is supported by the commit message, but the provided snippets do not show the internals of `nft::checkTrustlineAuthorized`, so details of freeze handling should remain bounded. Protocol security invariant: NFT offer acceptance involving non-native issued assets must enforce trustline authorization for each affected IOU recipient or holder covered by the transaction path before the offer acceptance proceeds. Verification notes: The patch does not by itself prove practical exploitability or economic theft. The evidence does not show arbitrary ledger writes outside NFT offer acceptance. The evidence does not prove a consensus failure, only a potential invariant violation around deep-frozen trustlines. The fix is feature-gated, so behavior depends on `fixEnforceNFTokenTrustlineV2` activation. No claim is made about native XRP paths because the added checks apply to non-native issued assets. Security classification is supported by explicit authorization checks added to transaction processing code. The finding is limited to NFT offer acceptance involving non-native issued assets. The behavior is feature-gated by `fixEnforceNFTokenTrustlineV2`. No exploitability beyond authorization bypass is proven by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final tags: `blockchain-core, transaction-processing, access-control, privilege-misuse, nft, trustline-authorization, issued-assets`

The supplied evidence supports retaining this as a security fix. The commit message explicitly describes NFT transactions bypassing trustline authorization, and the patch adds feature-gated `nft::checkTrustlineAuthorized` checks in `NFTokenAcceptOffer::preclaim` for non-native issued-asset paths including broker fees, buy-offer acceptance, and sell-offer acceptance. This is a transaction-processing authorization enforcement gap, not merely cleanup or reliability work. The original `signature` tag is not supported by the evidence and should be removed.

## Security Evidence

1. Commit body states the change fixes NFT transactions bypassing trustline authorization requirements.
2. Patch adds `nft::checkTrustlineAuthorized` checks before NFT offer acceptance proceeds on non-native issued assets.
3. New checks cover broker fee receipt, buy-offer owner authorization, and sell-offer non-native payment handling.
4. Failures from the authorization checks are returned immediately, blocking transaction processing.

## Missing Evidence

1. No full implementation of `nft::checkTrustlineAuthorized` is shown.
2. No regression test details are included in the supplied evidence.
3. Deep-freeze invariant impact is asserted by the commit message but not directly demonstrated by the snippets.
4. No concrete exploit scenario, theft, or consensus failure is proven from the patch alone.

## Claim Boundaries

1. Limited to NFT offer acceptance paths involving non-native issued assets.
2. Behavior is gated by `fixEnforceNFTokenTrustlineV2`.
3. Evidence supports authorization bypass prevention, not arbitrary ledger writes or signature validation issues.
4. Do not claim proven economic loss or practical exploitability beyond the trustline authorization bypass.
