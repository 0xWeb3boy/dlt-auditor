# Validation Card

## Metadata

- ID: `rippled-2022-06-22-rippled-transaction-processing-8266d9d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `negative-amount-validation`

## What Confirmed The Issue

- Evidence 1: NFTokenCreateOffer::preflight now rejects amount.negative() with temBAD_AMOUNT when fixNFTokenNegOffer is enabled.
- Evidence 2: Commit metadata states negative NFT offers were incorrectly allowed and brokered offers would improperly succeed.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path is shown beyond brokered negative offers improperly succeeding.
- Compensating control 2: No ledger-state consequence of a successful negative brokered offer is provided.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: invalid-transaction-acceptance, protocol-invariant-enforcement
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No concrete exploit path is shown beyond brokered negative offers improperly succeeding.
- Caution 2: No ledger-state consequence of a successful negative brokered offer is provided.
