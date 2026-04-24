# Root-Cause Card

## Metadata

- ID: `optimism-2022-06-22-optimism-transaction-processing-a828da9fe7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Privileged oracle roles should be explicit and observable: the contract deployment path, role-query interface, and role-rotation path should clearly encode who operates the oracle and who administers that role.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: privilege-misuse
- Secondary impact: state-integrity

## Short Reusable Lesson

- Privileged oracle roles should be explicit and observable: the contract deployment path, role-query interface, and role-rotation path should clearly encode who operates the oracle and who administers that role. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce authorization at the boundary and fail closed before state, privilege, or consensus-visible output changes.
