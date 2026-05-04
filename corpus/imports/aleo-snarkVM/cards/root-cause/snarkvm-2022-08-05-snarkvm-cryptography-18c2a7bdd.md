# Root-Cause Card

## Metadata

- ID: `snarkvm-2022-08-05-snarkvm-cryptography-18c2a7bdd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-ledger-lookup`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fail-closed-error-handling`

## Violated Invariant

- Invariant: A ledger query that classifies spend state must distinguish lookup errors from confirmed absence and must not report spendable state on uncertainty.

## Trust Boundary

- Boundary: ledger store result -> record scanner classification

## Attack Surface

- Entrypoint type: ledger-query-path
- Sensitive sink: unspent output record returned to wallet or caller

## Impact Pattern

- Primary impact: fail-closed ledger classification
- Secondary impact: client safety and wallet correctness

## Short Reusable Lesson

- Security-sensitive query helpers should treat backend errors as unknown, not as proof that a spend marker is absent.
