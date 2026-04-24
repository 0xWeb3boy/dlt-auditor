# Code-Shape Card

## Metadata

- ID: `rippled-2026-01-15-rippled-transaction-processing-c0b671206`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rounding-accounting-yield-theft`

## Code Shape Summary

- Likely security fix in rippled's lending LoanPay path. The strongest evidence is the commit message saying a new test covers "Yield Theft via Rounding Manipulation" and now verifies no yield theft occurs, together with changes around rounded vault payments, assets-... Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact accounting-integrity check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Make post-rounding accounting state explicit, validate local vault-accounting invariants after rounding, handle zero-or-rounded-to-zero payment cases gracefully, and add regression coverage for the rounding-manipulation scenario.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Make post-rounding accounting state explicit, validate local vault-accounting invariants after rounding, handle zero-or-rounded-to-zero payment cases gracefully, and add regression coverage for the rounding-manipulation scenario.

## False Match Warnings

- Full regression test body is not provided.
- Exact STAmount.h and LendingHelpers.cpp changes are not shown.
