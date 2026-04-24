# Code-Shape Card

## Metadata

- ID: `rippled-2025-10-21-rippled-transaction-processing-83ee3788e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-reserve-check`

## Code Shape Summary

- The patch fixes VaultWithdraw validation around implicit self-destination handling and reserve enforcement before creating a non-native holding. Reusable shape: check for reserve-enforcement was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact reserve-enforcement check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Resolve the effective destination consistently, then apply destination-account policy and reserve checks before creating ledger owner objects.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the reserve-enforcement gate runs before the state-changing branch.

## Patch Pattern

- Resolve the effective destination consistently, then apply destination-account policy and reserve checks before creating ledger owner objects.

## False Match Warnings

- No exploit scenario or proof of abuse impact is provided.
- No evidence shows direct fund theft, authorization bypass, consensus failure, or memory safety impact.
