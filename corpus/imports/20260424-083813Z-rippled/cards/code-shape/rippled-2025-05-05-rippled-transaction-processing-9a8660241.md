# Code-Shape Card

## Metadata

- ID: `rippled-2025-05-05-rippled-transaction-processing-9a8660241`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant-hardening`

## Code Shape Summary

- The evidence supports an accounting correctness and invariant-hardening change in rippled's lending loan/vault transaction path. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact accounting-integrity check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize domain accounting calculations, add explicit sufficient-balance checks before ledger-field decrements, and add final invariant checks for negative loan accounting fields.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Centralize domain accounting calculations, add explicit sufficient-balance checks before ledger-field decrements, and add final invariant checks for negative loan accounting fields.

## False Match Warnings

- No demonstrated attacker-controlled transaction sequence is provided.
- No proof of asset loss, unauthorized transfer, consensus failure, or node crash is shown.
