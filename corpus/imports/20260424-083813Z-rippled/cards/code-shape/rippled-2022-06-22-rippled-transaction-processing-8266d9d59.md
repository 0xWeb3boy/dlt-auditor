# Code-Shape Card

## Metadata

- ID: `rippled-2022-06-22-rippled-transaction-processing-8266d9d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `negative-amount-validation`

## Code Shape Summary

- The patch adds an amendment-gated rejection of negative NFT offer amounts in NFTokenCreateOffer::preflight. Reusable shape: check for numeric-bounds was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact numeric-bounds check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit transaction preflight validation for an invalid economic value, gated by a protocol amendment, before downstream matching or acceptance logic can process the offer.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the numeric-bounds gate runs before the state-changing branch.

## Patch Pattern

- Add explicit transaction preflight validation for an invalid economic value, gated by a protocol amendment, before downstream matching or acceptance logic can process the offer.

## False Match Warnings

- No concrete exploit path is shown beyond brokered negative offers improperly succeeding.
- No ledger-state consequence of a successful negative brokered offer is provided.
