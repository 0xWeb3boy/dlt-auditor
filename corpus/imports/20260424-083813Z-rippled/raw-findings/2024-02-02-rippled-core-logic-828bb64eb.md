---
case_id: case_20240202_828bb64eb
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - state-accounting
  - economic-distortion
source_quality: high
date: 2024-02-02
source_refs:
  - git:828bb64ebc76394cf9a3f7edd42f4588d106932f
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:302"
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:476"
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:388"
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.h:39"
bug_class: reserve-enforcement-bypass
confidence: medium
tags:
  - blockchain-core
  - core-logic
  - nft
  - reserve-enforcement
  - state-accounting
  - consensus-rule
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a protocol reserve-enforcement fix in rippled's NFTokenAcceptOffer sell-offer path. The commit states that, before the fixNFTokenReserve amendment, an NFTokenAcceptOffer transaction could succeed when the NFT recipient lacked sufficient reserve for a new NFTokenPage. The code snippets show the affected NFT transfer paths being centralized through transferNFToken, and the commit body states that the amendment checks OwnerCount changes and fails with tecINSUFFICIENT_RESERVE when the new reserve requirement is not met.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp`, the patch replaces `NFTokenAcceptOffer::acceptOffer(std::shared_ptr<SLE> const& offer)` with `NFTokenAcceptOffer::transferNFToken(`.

2. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp`, the patch replaces `auto tokenAndPage = nft::findTokenAndPage(view(), seller, nftokenID);` with `// Now transfer the NFT:`.

3. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp`, the patch replaces `auto tokenAndPage = nft::findTokenAndPage(view(), seller, nftokenID);` with `return transferNFToken(buyer, seller, nftokenID);`.

4. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.h`, the patch replaces `public:` with `TER`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/ripple/app/tx/impl/NFTokenBurn.cpp`, `src/ripple/app/tx/impl/applySteps.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/NFTokenBurn.cpp`, `src/ripple/app/tx/impl/details/NFTokenUtils.h`. The strongest project-level identifiers around this patch are `const`, `nft::findTokenAndPage`, `nft::removeToken`, and `seller`.

## Before/After Behavior

Before the patch, non-brokered NFT sell-offer acceptance could move an NFT to a recipient even when the recipient did not have enough reserve for the resulting NFTokenPage or OwnerCount increase. After the patch, the affected NFTokenAcceptOffer transfer paths call transferNFToken, and under the fixNFTokenReserve amendment the transaction checks the post-transfer reserve requirement and can fail with tecINSUFFICIENT_RESERVE.

# Root Cause

The NFTokenAcceptOffer sell-offer path did not consistently enforce the recipient's reserve requirement when accepting the NFT caused a new NFTokenPage or OwnerCount increase. The supported scope is the non-brokered sell-offer path without a buy offer.

## Walkthrough

1. An NFTokenAcceptOffer transaction accepts an NFT sell offer with a buyer, seller, and nftokenID.

2. Before the patch, the affected paths performed the NFT movement inline by finding the seller's token page, removing the token, and inserting it for the buyer.

3. The commit states that this could succeed even when the buyer lacked enough reserve for a new NFTokenPage.

4. The patch introduces a private transferNFToken helper and routes the affected acceptOffer and doApply transfer points through it.

5. The commit states that the fixNFTokenReserve amendment checks whether OwnerCount changed and then validates the new reserve requirement.

6. When the reserve requirement is not met, the transaction should now fail with tecINSUFFICIENT_RESERVE.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp | 302 | Introduces centralized NFToken transfer helper for removing the token from the seller and inserting it for the buyer, the state transition that can change NFTokenPage ownership/reserve burden. |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp | 388 | acceptOffer sell-offer path now delegates NFT movement through transferNFToken, placing the direct sell acceptance path under the amended transfer/reserve handling. |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp | 476 | doApply path for offer acceptance delegates final NFT transfer through transferNFToken after payment handling. |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.h | 39 | Declares the private transferNFToken helper used by NFTokenAcceptOffer transaction paths. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:302` (updates aggregate accounting or lifecycle state)

Before
```cpp
}

TER
NFTokenAcceptOffer::acceptOffer(std::shared_ptr<SLE> const& offer)
```
After
```cpp
}

TER
NFTokenAcceptOffer::transferNFToken(
    AccountID const& buyer,
    AccountID const& seller,
    uint256 const& nftokenID)
{
```

## Snippet 2

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:476` (updates aggregate accounting or lifecycle state)

Before
```cpp
}

        auto tokenAndPage = nft::findTokenAndPage(view(), seller, nftokenID);

        if (!tokenAndPage)
            return tecINTERNAL;

        if (auto const ret = nft::removeToken(
```
After
```cpp
}

        // Now transfer the NFT:
        return transferNFToken(buyer, seller, nftokenID);
    }
```

## Snippet 3

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:388` (updates aggregate accounting or lifecycle state)

Before
```cpp
// Now transfer the NFT:
    auto tokenAndPage = nft::findTokenAndPage(view(), seller, nftokenID);

    if (!tokenAndPage)
        return tecINTERNAL;

    if (auto const ret = nft::removeToken(
```
After
```cpp
// Now transfer the NFT:
    return transferNFToken(buyer, seller, nftokenID);
}
```

## Snippet 4

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.h:39` (updates aggregate accounting or lifecycle state)

Before
```c
std::shared_ptr<SLE> const& sell);

public:
    static constexpr ConsequencesFactoryType ConsequencesFactory{Normal};
```
After
```c
std::shared_ptr<SLE> const& sell);

    TER
    transferNFToken(
        AccountID const& buyer,
        AccountID const& seller,
        uint256 const& nfTokenID);
```

# Fix Pattern

Centralize the NFT ownership transfer point and enforce the recipient's post-transfer reserve requirement when the transfer changes OwnerCount or NFTokenPage burden.

## How It Was Fixed

The patch adds NFTokenAcceptOffer::transferNFToken and rewires the affected NFT sell-offer acceptance paths to use it. The commit description states that the amendment adds an OwnerCount-change check followed by a reserve check, returning tecINSUFFICIENT_RESERVE when appropriate.

# Why It Matters

1. Preserves the ledger reserve invariant for NFT ownership state.

2. Prevents a recipient from acquiring NFT page burden without sufficient reserve.

3. Keeps the confirmed scope limited to non-brokered NFT sell-offer acceptance without a buy offer.

4. Does not establish theft, memory corruption, or a general reserve bypass across unrelated transaction types.

# Evidence Notes

The strongest evidence is the commit body, which explicitly describes the insufficient-reserve acceptance bug, the affected NFTokenAcceptOffer mode, and the intended tecINSUFFICIENT_RESERVE failure. The supplied code snippets show transfer centralization in src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp and the helper declaration in NFTokenAcceptOffer.h. The snippets do not independently show the full reserve-check implementation, so claims should stay scoped to the behavior described by the commit. Protocol security invariant: Accepting an NFT sell offer must not leave the recipient with an increased NFTokenPage or OwnerCount reserve burden unless the account satisfies the resulting reserve requirement. Verification notes: The provided evidence does not prove direct theft of funds or NFTs. The commit states brokered mode and paths involving a buy offer were not affected. The evidence supports a reserve enforcement bypass for NFT sell-offer acceptance, not a general reserve bypass across all transaction types. The snippets mainly show transfer centralization; the reserve-check details are established by the commit description rather than fully visible changed lines. No claim is made about remote code execution, memory corruption, or signature/authentication bypass. Commit message directly identifies the reserve bypass and expected failure code. Changed files include NFTokenAcceptOffer implementation and tests. Provided snippets support the affected transfer path but not broader transaction-type impact. No evidence supports claims of NFT theft, fund theft, RCE, memory corruption, or authentication bypass. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reserve-enforcement-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, core-logic, nft, reserve-enforcement, state-accounting, consensus-rule`

The supplied evidence supports retaining this as a security-relevant protocol hardening case, but the original `security-fix`/high-confidence framing is stronger than the visible patch evidence alone. The commit message explicitly describes an NFT sell-offer acceptance path allowing success without sufficient account reserve and says the amendment adds post-transfer reserve checks. The shown code evidence mainly demonstrates centralizing NFT transfer paths through `transferNFToken`, not the full reserve-check implementation, so this is best validated as reserve-enforcement hardening rather than a fully proven exploitable security fix.

## Security Evidence

1. Commit body states `NFTokenAcceptOffer` could succeed when the recipient lacked sufficient reserves for a new `NFTokenPage`.
2. Commit body states the corrected behavior is failure with `tecINSUFFICIENT_RESERVE`.
3. Changed implementation is in the core transaction path for NFT offer acceptance.
4. Patch routes affected NFT transfer points through a centralized `transferNFToken` helper.
5. Commit introduces an amendment feature and test changes, suggesting consensus-visible behavior correction.

## Missing Evidence

1. Provided snippets do not show the actual OwnerCount or reserve-check logic.
2. No supplied evidence demonstrates theft, unauthorized transfer, or direct fund loss.
3. No full regression test content is provided.
4. Exploitability beyond avoiding required reserve is not established from the patch excerpts.

## Claim Boundaries

1. Supported scope is NFTokenAcceptOffer sell-offer acceptance where recipient reserve requirements may increase.
2. Do not generalize this to all NFT transactions or all reserve enforcement paths.
3. Do not claim memory corruption, authentication bypass, signature bypass, or remote code execution.
4. Brokered mode and paths involving a buy offer are explicitly outside the affected scope per the commit body.
