# Code-Shape Card

## Metadata

- ID: `rippled-2025-11-14-rippled-core-logic-362ecbd1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting`

## Code Shape Summary

- The supported finding is reserve underaccounting for vault pseudo-accounts, not an authorization flaw. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact accounting-integrity check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Make reserve accounting match the number of persistent ledger objects created and destroyed, and add ledger consistency checks before deleting related state.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Make reserve accounting match the number of persistent ledger objects created and destroyed, and add ledger consistency checks before deleting related state.

## False Match Warnings

- No demonstrated exploit path showing network-level denial of service or ledger bloat at scale.
- No evidence of unauthorized vault access, asset theft, withdrawal, or takeover.
