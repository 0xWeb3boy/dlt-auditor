# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-03-20-stellar-core-storage-cc9a3c0bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`

## Code Shape Summary

- The operation apply branch loaded an existing trustline and assigned a new limit without first comparing it to zero and current balance.

## Search Motifs

- trustline limit assigned directly from operation input
- limit below balance not rejected
- negative asset limit accepted
- new INVALID_LIMIT result code

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Add a transaction-level guard for nonnegative and balance-compatible trustline limits before mutating ledger state, with a specific invalid-limit result.

## False Match Warnings

- Creating a new empty trustline with a zero limit may be valid in some protocols.
- A separate pre-validation function may already enforce the same limit and balance relation.
- Native currency balances may have different limit semantics than issued-asset trustlines.
