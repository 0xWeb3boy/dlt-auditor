# Code-Shape Card

## Metadata

- ID: `rippled-2018-03-02-rippled-transaction-processing-8d9dffcf8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `escrow-condition-validation-hardening`

## Code Shape Summary

- The patch changes XRP Ledger escrow creation and finish semantics under the fix1571 amendment. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact input-and-state-invariant-validation check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an amendment-gated validation rule that rejects ambiguous escrow creation states, and align apply-time timing checks with the revised escrow semantics.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Add an amendment-gated validation rule that rejects ambiguous escrow creation states, and align apply-time timing checks with the revised escrow semantics.

## False Match Warnings

- No evidence of theft, unauthorized signature use, cryptocondition bypass, or ledger corruption is provided.
- The commit says the prior immediate-finish behavior was documented, which weakens a concrete vulnerability claim.
