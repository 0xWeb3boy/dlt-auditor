# Code-Shape Card

## Metadata

- ID: `rippled-2025-11-04-rippled-core-logic-aed8e2b16`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant-enforcement`

## Code Shape Summary

- The patch is plausibly security-relevant because it adds an explicit transaction failure when LoanPay would leave vault accounting in an invalid state. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact accounting-integrity check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit fail-closed validation for a post-update accounting invariant and centralize related loan setup guard checks.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Add explicit fail-closed validation for a post-update accounting invariant and centralize related loan setup guard checks.

## False Match Warnings

- No proof that an external user can trigger the invalid accounting state.
- No demonstrated fund theft, minting, loss, freezing, or user-visible balance corruption.
