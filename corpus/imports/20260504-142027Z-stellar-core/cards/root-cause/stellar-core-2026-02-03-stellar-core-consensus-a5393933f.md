# Root-Cause Card

## Metadata

- ID: `stellar-core-2026-02-03-stellar-core-consensus-a5393933f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consistent-host-function-validation`

## Violated Invariant

- Invariant: Every transaction admission and transaction-set validation boundary must apply the same host-function validity checks, including through wrapper transaction types.

## Trust Boundary

- Boundary: submitted-soroban-transaction -> consensus-admission-and-txset-validation

## Attack Surface

- Entrypoint type: transaction-admission-and-consensus-validation
- Sensitive sink: transaction queue acceptance and transaction-set validity decision
- Attacker capability: Submit Soroban or fee-bump-wrapped transactions with malformed host-function fields.
- Main precondition: Some admission path returns pending without validateHostFn.

## Impact Pattern

- Primary impact: consensus-validation-hardening
- Secondary impact: transaction-integrity, mempool-consistency
- Severity guess: medium because Missing validation at consensus-adjacent boundaries is security relevant, but the exact malformed condition and exploit impact are not proven.

## Short Reusable Lesson

- Consensus-adjacent validation must be uniform across wrappers and admission paths; partial validation creates policy gaps even when individual checks exist elsewhere.
