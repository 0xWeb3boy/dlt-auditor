---
case_id: case_20220622_8266d9d59
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2022-06-22
source_refs:
  - git:8266d9d598d19f05e1155956b30ca443c27e119e
  - "src/ripple/app/tx/impl/NFTokenCreateOffer.cpp:83"
  - "src/ripple/app/tx/impl/NFTokenCreateOffer.cpp:47"
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:110"
  - "src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:157"
bug_class: negative-amount-validation
impact_type:
  - invalid-transaction-acceptance
  - protocol-invariant-enforcement
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - nft-offers
  - amount-validation
  - protocol-amendment
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an amendment-gated rejection of negative NFT offer amounts in NFTokenCreateOffer::preflight. The strongest supported claim is that negative sfAmount values were previously not explicitly rejected at creation time and, according to the commit message, brokered offers could improperly succeed while direct offers failed differently. The Destination changes are related behavior changes under the same amendment, but they are not established as the root vulnerability by the supplied evidence.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/NFTokenCreateOffer.cpp`, the patch replaces `// The destination field is only valid on a sell offer; it makes no` with `// Some folks think it makes sense for a buy offer to specify a`.

2. In `src/ripple/app/tx/impl/NFTokenCreateOffer.cpp`, the patch replaces `auto const amount = ctx.tx[sfAmount];` with `STAmount const amount = ctx.tx[sfAmount];`.

3. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp`, the patch replaces `// If the seller specified a destination, that destination must be` with `// If the buyer specified a destination, that destination must be`.

4. In `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp`, the patch replaces `// The account offering to buy must have funds:` with `// If not in bridged mode...`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/app/tx/impl/OfferStream.h`, `src/ripple/app/tx/impl/OfferStream.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/Transactor.cpp`, `src/ripple/app/tx/impl/Escrow.cpp`. The strongest project-level identifiers around this patch are `dest`, `offer`, `auto`, and `const`.

## Before/After Behavior

Before the patch, the shown NFTokenCreateOffer::preflight amount block did not reject amount.negative() before continuing to later checks, and the commit message states that negative NFT offers could be created and handled inconsistently. After the patch, when fixNFTokenNegOffer is enabled, negative sfAmount values return temBAD_AMOUNT during preflight. Separately, buy offers with Destination are allowed after the amendment and NFTokenAcceptOffer::preclaim adds constraints on who the destination may be in brokered or direct acceptance paths.

# Root Cause

The NFT offer creation path lacked an explicit preflight check rejecting negative sfAmount values, allowing invalid economic input to reach downstream NFT offer handling.

## Walkthrough

1. NFTokenCreateOffer::preflight validates NFT offer creation inputs, including sfAmount.

2. The before evidence shows the amount was read and then processed without the newly added amount.negative() rejection.

3. The commit message states that negative NFT offers were incorrectly allowed and that brokered offers could improperly succeed.

4. The patch adds an amendment-gated check returning temBAD_AMOUNT for negative amounts.

5. The patch also changes buy-offer Destination handling under the same amendment, allowing Destination on buy offers after activation.

6. NFTokenAcceptOffer::preclaim adds Destination constraints for brokered and direct buy-offer acceptance paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/NFTokenCreateOffer.cpp | 47 | Adds amendment-gated rejection of negative sfAmount values during NFTokenCreateOffer preflight. |
| src/ripple/app/tx/impl/NFTokenCreateOffer.cpp | 83 | Changes Destination validation for buy offers under fixNFTokenNegOffer, allowing broker targeting after the amendment. |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp | 110 | Validates buy-offer Destination in brokered matching so it must name the seller or broker. |
| src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp | 157 | Validates direct buy-offer Destination so only the destination account may accept outside bridged mode. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/NFTokenCreateOffer.cpp:83` (changes a sensitive control or state-update path)

Before
```cpp
if (auto dest = ctx.tx[~sfDestination])
    {
        // The destination field is only valid on a sell offer; it makes no
        // sense in a buy offer.
        if (!isSellOffer)
            return temMALFORMED;
```
After
```cpp
if (auto dest = ctx.tx[~sfDestination])
    {
        // Some folks think it makes sense for a buy offer to specify a
        // specific broker using the Destination field.  This change doesn't
        // deserve it's own amendment, so we're piggy-backing on
        // fixNFTokenNegOffer.
        //
        // Prior to fixNFTokenNegOffer any use of the Destination field on
```

## Snippet 2

Context: `src/ripple/app/tx/impl/NFTokenCreateOffer.cpp:47` (changes a sensitive control or state-update path)

Before
```cpp
{
        auto const amount = ctx.tx[sfAmount];

        if (!isXRP(amount))
```
After
```cpp
{
        STAmount const amount = ctx.tx[sfAmount];

        if (amount.negative() && ctx.rules.enabled(fixNFTokenNegOffer))
            // An offer for a negative amount makes no sense.
            return temBAD_AMOUNT;
```

## Snippet 3

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:110` (changes a sensitive control or state-update path)

Before
```cpp
return tecINSUFFICIENT_PAYMENT;

        // If the seller specified a destination, that destination must be
        // the buyer or the broker.
```
After
```cpp
return tecINSUFFICIENT_PAYMENT;

        // If the buyer specified a destination, that destination must be
        // the seller or the broker.
        if (auto const dest = bo->at(~sfDestination))
        {
            if (*dest != so->at(sfOwner) && *dest != ctx.tx[sfAccount])
                return tecNFTOKEN_BUY_SELL_MISMATCH;
```

## Snippet 4

Context: `src/ripple/app/tx/impl/NFTokenAcceptOffer.cpp:157` (changes a sensitive control or state-update path)

Before
```cpp
return tecNO_PERMISSION;

        // The account offering to buy must have funds:
        auto const needed = bo->at(sfAmount);
```
After
```cpp
return tecNO_PERMISSION;

        // If not in bridged mode...
        if (!so)
        {
            // If the offer has a Destination field, the acceptor must be the
            // Destination.
            if (auto const dest = bo->at(~sfDestination);
```

# Fix Pattern

Add explicit transaction preflight validation for an invalid economic value, gated by a protocol amendment, before downstream matching or acceptance logic can process the offer.

## How It Was Fixed

The fix introduces fixNFTokenNegOffer and adds a check in NFTokenCreateOffer::preflight: if sfAmount is negative and the amendment is enabled, the transaction returns temBAD_AMOUNT. Related Destination handling for buy offers is also updated under the same amendment with acceptance-time validation in NFTokenAcceptOffer::preclaim.

# Why It Matters

1. Negative NFT offer amounts are invalid economic values.

2. Brokered acceptance previously had a path described as improperly succeeding.

3. Preflight rejection gives a clear malformed-transaction result before later processing.

4. The evidence does not prove theft, inflation, or consensus failure.

# Evidence Notes

Supported by the commit message and the shown hunks in NFTokenCreateOffer::preflight adding amount.negative() rejection. The evidence supports a protocol validation flaw in NFT offer handling, but does not establish concrete exploit impact beyond brokered negative-amount offers improperly succeeding. Destination-related changes are support/behavior expansion and should not be treated as the primary vulnerability without more evidence. Protocol security invariant: NFToken offer creation should reject negative sfAmount values before an offer can be created or accepted, so brokered and direct offer paths cannot process nonsensical economic values differently. Verification notes: The patch does not prove theft, fund inflation, or consensus failure by itself. The exact ledger-state consequences of a brokered negative-amount offer are not shown beyond improper success. The Destination changes include API/behavior expansion and should not be treated as the primary vulnerability without more evidence. No exploit preconditions, attacker workflow, or affected deployed amendment state are established by the provided patch evidence. No claim of theft or fund inflation is supported by the provided evidence. No exploit workflow or deployed activation state is established. The negative-amount rejection is the grounded security-relevant fix. Destination handling should be described as related amendment behavior, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `negative-amount-validation`
Final impact type: `invalid-transaction-acceptance, protocol-invariant-enforcement`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, nft-offers, amount-validation, protocol-amendment`

The supplied evidence supports retaining this as security hardening, but not as a proven security-fix with concrete exploit impact. The patch adds amendment-gated rejection of negative NFT offer amounts in transaction preflight, and the commit message states brokered offers could improperly succeed. That is security-relevant in a blockchain transaction-processing path because it enforces an economic validity invariant before offer acceptance. However, the evidence does not establish theft, inflation, consensus failure, or a detailed attacker workflow.

## Security Evidence

1. NFTokenCreateOffer::preflight now rejects amount.negative() with temBAD_AMOUNT when fixNFTokenNegOffer is enabled.
2. Commit metadata states negative NFT offers were incorrectly allowed and brokered offers would improperly succeed.
3. The change is in transaction creation and acceptance logic for NFT offers, a security-sensitive economic validation path.
4. NFTokenAcceptOffer adds Destination checks that constrain who may accept buy offers with a Destination field.

## Missing Evidence

1. No concrete exploit path is shown beyond brokered negative offers improperly succeeding.
2. No ledger-state consequence of a successful negative brokered offer is provided.
3. No evidence of fund theft, inflation, denial of service, or consensus divergence is shown.
4. No deployment or amendment activation context is provided.

## Claim Boundaries

1. Treat the negative-amount rejection as the validated security-relevant change.
2. Treat Destination handling as related behavior under the same amendment, not the primary vulnerability.
3. Do not claim theft, asset creation, inflation, or consensus failure from the supplied evidence.
4. Classify as security hardening because the patch enforces a protocol validity invariant without proving concrete exploit impact.
