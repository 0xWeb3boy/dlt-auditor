# Validation Card

## Metadata

- ID: `rippled-2023-03-20-rippled-transaction-processing-305c9a8d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identifier-collision`

## What Confirmed The Issue

- Evidence 1: Commit body gives concrete reproducible remint scenarios that create the same NFTokenID.
- Evidence 2: NFTokenMint.cpp changes the NFT sequence basis under fixNFTokenRemint instead of relying only on MintedNFTokens.

## What Could Have Invalidated It

- Compensating control 1: No supplied evidence proves asset theft, direct monetary loss, or marketplace exploitation.
- Compensating control 2: No supplied evidence proves consensus failure beyond duplicate NFT identity/state integrity risk.

## Severity Guidance

- Expected impact band: security-impact: state-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No supplied evidence proves asset theft, direct monetary loss, or marketplace exploitation.
- Caution 2: No supplied evidence proves consensus failure beyond duplicate NFT identity/state integrity risk.
