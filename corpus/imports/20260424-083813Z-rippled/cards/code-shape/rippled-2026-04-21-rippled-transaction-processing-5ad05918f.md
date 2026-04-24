# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-21-rippled-transaction-processing-5ad05918f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-structural-validation`

## Code Shape Summary

- The patch fixes a validation gap for Permissioned DEX hybrid offers: the old invariant rejected missing sfAdditionalBooks and arrays larger than one, but did not reject an empty sfAdditionalBooks array when the field was present. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact input-and-state-invariant-validation check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace a partial structural validation predicate with an exact cardinality check, gated by the protocol amendment so legacy and post-fix behavior remain distinct.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Replace a partial structural validation predicate with an exact cardinality check, gated by the protocol amendment so legacy and post-fix behavior remain distinct.

## False Match Warnings

- No evidence shows how an empty sfAdditionalBooks hybrid offer could be created or accepted into the ledger.
- No evidence demonstrates theft, fund loss, unauthorized trading, or economic distortion.
