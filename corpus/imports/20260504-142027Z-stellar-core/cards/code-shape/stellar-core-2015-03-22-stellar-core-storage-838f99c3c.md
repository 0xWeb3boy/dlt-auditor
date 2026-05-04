# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-03-22-stellar-core-storage-838f99c3c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trustline-invariant-enforcement`

## Code Shape Summary

- Transaction handlers performed direct TrustLineEntry.balance arithmetic across payment and offer paths instead of using a checked helper.

## Search Motifs

- getTrustLine().balance += amount
- getTrustLine().balance -= amount
- payment to unauthorized trustline
- helper addBalance introduced for trustline mutations

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Centralize trustline balance mutation in a helper that rejects over-limit and negative results, then replace direct transaction-path arithmetic and add destination authorization checks.

## False Match Warnings

- Direct arithmetic inside the checked helper itself is expected.
- Look for evidence that negative balances or over-limit balances can persist, not just temporary arithmetic.
- Authorization checks may live in issuer-specific pre-validation code.
