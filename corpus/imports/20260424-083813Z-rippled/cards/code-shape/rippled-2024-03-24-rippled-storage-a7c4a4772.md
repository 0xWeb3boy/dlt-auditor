# Code-Shape Card

## Metadata

- ID: `rippled-2024-03-24-rippled-storage-a7c4a4772`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `amm-offer-overflow-hardening`

## Code Shape Summary

- The patch appears to fix incorrect handling of large synthetic AMM offers in rippled's payment AMM path. Reusable shape: check for numeric-bounds was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-storage-or-ledger-update-path missing exact numeric-bounds check before persistent ledger state, object index, cache, or history consistency
- Motif 2: security-sensitive path reaches persistent ledger state, object index, cache, or history consistency before rejecting malformed, stale, or unauthorized input
- Motif 3: Make large synthetic AMM offer construction rules-aware and optional, avoid retrying max-offer construction after overflow under the new feature flag, and add an explicit AMM pool-product invariant check.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into persistent ledger state, object index, cache, or history consistency unless the numeric-bounds gate runs before the state-changing branch.

## Patch Pattern

- Make large synthetic AMM offer construction rules-aware and optional, avoid retrying max-offer construction after overflow under the new feature flag, and add an explicit AMM pool-product invariant check.

## False Match Warnings

- No exploit reproduction or attack scenario is provided.
- No implementation of checkInvariant is shown in the supplied evidence.
