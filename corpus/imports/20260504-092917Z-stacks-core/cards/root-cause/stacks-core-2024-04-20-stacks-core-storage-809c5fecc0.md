# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-04-20-stacks-core-storage-809c5fecc0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-error-propagation-transaction-validity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-validation`

## Violated Invariant

- Invariant: Protocol inputs must be normalized and validated in their canonical context before they influence state, signatures, or consensus outcomes.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: transaction-validity
- Secondary impact: state-integrity

## Short Reusable Lesson

- The patch likely fixes a consensus-relevant STX transfer rollback bug in the Clarity VM. The grounded change is a one-character error-propagation fix in `Environment::stx_transfer`: `value.clone().expect_result()` became `value.clone().expect_result()?`. Given the surrounding code, this means the commit/rollback decision now matches the inner Clarity response result, committing only for inner `Ok(_)`.
