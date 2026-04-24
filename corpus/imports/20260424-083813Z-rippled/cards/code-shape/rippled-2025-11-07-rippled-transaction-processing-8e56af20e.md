# Code-Shape Card

## Metadata

- ID: `rippled-2025-11-07-rippled-transaction-processing-8e56af20e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-representability-hardening`

## Code Shape Summary

- The patch separates Number validity from representability and adds explicit representability checks for vault aggregate fields. Reusable shape: check for numeric-bounds was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact numeric-bounds check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Separate validity from representability, add an explicit representability predicate, and enforce it at the vault invariant boundary for aggregate ledger amounts.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the numeric-bounds gate runs before the state-changing branch.

## Patch Pattern

- Separate validity from representability, add an explicit representability predicate, and enforce it at the vault invariant boundary for aggregate ledger amounts.

## False Match Warnings

- No concrete pre-patch transaction sequence reaches an unrepresentable vault value.
- No demonstrated exploit path, theft, unauthorized balance creation, or consensus split is shown.
