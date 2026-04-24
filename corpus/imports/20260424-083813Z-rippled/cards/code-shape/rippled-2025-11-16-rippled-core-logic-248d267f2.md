# Code-Shape Card

## Metadata

- ID: `rippled-2025-11-16-rippled-core-logic-248d267f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-validation`

## Code Shape Summary

- The evidence supports a vault numeric-validation change, not an established vulnerability fix. Reusable shape: check for numeric-bounds was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact numeric-bounds check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit numeric validity and representability checks around vault amount inputs and post-apply vault accounting state.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the numeric-bounds gate runs before the state-changing branch.

## Patch Pattern

- Add explicit numeric validity and representability checks around vault amount inputs and post-apply vault accounting state.

## False Match Warnings

- No exploit path is shown.
- No demonstrated funds loss, unauthorized action, or privilege bypass is shown.
