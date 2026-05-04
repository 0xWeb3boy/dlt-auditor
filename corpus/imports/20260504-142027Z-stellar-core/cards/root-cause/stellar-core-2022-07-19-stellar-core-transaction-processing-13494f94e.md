# Root-Cause Card

## Metadata

- ID: `stellar-core-2022-07-19-stellar-core-transaction-processing-13494f94e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-order-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-transaction-set-ordering`

## Violated Invariant

- Invariant: Transaction sets must preserve canonical hash ordering after every filtering or mutation step and validation must reject unsorted sets.

## Trust Boundary

- Boundary: candidate-transaction-set -> consensus-transaction-set-validation

## Attack Surface

- Entrypoint type: consensus-or-mempool-txset-validation
- Sensitive sink: accepted transaction-set ordering used for deterministic processing
- Attacker capability: Provide or influence candidate transaction sets.
- Main precondition: Filtered transaction vectors are stored without re-sorting.

## Impact Pattern

- Primary impact: consensus-determinism
- Secondary impact: transaction-order-integrity, validation-hardening
- Severity guess: medium because Canonical ordering affects deterministic processing, but evidence does not prove an exploit beyond ordering hardening and test failures.

## Short Reusable Lesson

- Canonical collection invariants must be restored after mutation, not just assumed from construction time.
