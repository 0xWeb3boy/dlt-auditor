# Code-Shape Card

## Metadata

- ID: `rippled-2025-03-11-rippled-core-logic-3715d7e2e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch likely fixes access-control bugs in vault deposit and shared MPToken authorization logic. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact authorization check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace exact flag comparisons with bitwise flag checks, make the shared authorization helper enforce the authorized-token bit consistently, and ensure required MPToken state is present on related deposit paths.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Replace exact flag comparisons with bitwise flag checks, make the shared authorization helper enforce the authorized-token bit consistently, and ensure required MPToken state is present on related deposit paths.

## False Match Warnings

- No advisory, issue discussion, or exploit report is provided.
- Tests are mentioned but their assertions are not included in the supplied evidence.
