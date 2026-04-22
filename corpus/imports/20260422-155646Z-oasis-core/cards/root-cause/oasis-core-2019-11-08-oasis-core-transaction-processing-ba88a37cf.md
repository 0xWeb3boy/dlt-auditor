# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-08-oasis-core-transaction-processing-ba88a37cf`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-validator-set-minimum-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `minimum-set-bounds`

## Violated Invariant

- Invariant: If scheduler configuration specifies a minimum validator count, initialization and validator election should reject validator sets smaller than that floor.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `validator set composition`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- If scheduler configuration specifies a minimum validator count, initialization and validator election should reject validator sets smaller than that floor. In this pattern, the shown code enforced only a non-empty validator election result, not a configured lower bound on validator-set size, and it did not validate that lower bound during initialization. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
