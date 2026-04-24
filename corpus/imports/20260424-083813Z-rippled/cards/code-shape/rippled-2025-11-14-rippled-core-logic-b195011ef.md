# Code-Shape Card

## Metadata

- ID: `rippled-2025-11-14-rippled-core-logic-b195011ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting`

## Code Shape Summary

- The supported finding is a Vault reserve-accounting fix, not an access-control issue. The patch changes Vault creation from accounting for one owner-reserved object to two, mirrors that on deletion, and adds validation before removing the Vault pseudo-account. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact accounting-integrity check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Make resource accounting match the actual number of persistent ledger objects, and validate dependent ledger objects before removing them.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Make resource accounting match the actual number of persistent ledger objects, and validate dependent ledger objects before removing them.

## False Match Warnings

- No evidence shows an authorization bypass or privilege misuse.
- No evidence demonstrates theft, unauthorized withdrawal, or direct asset loss.
