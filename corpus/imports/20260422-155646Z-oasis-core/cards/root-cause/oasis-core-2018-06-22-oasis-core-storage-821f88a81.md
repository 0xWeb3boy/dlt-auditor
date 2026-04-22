# Root-Cause Card

## Metadata

- ID: `oasis-core-2018-06-22-oasis-core-storage-821f88a81`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `role-accounting`

## Violated Invariant

- Invariant: Aggregation should account for commitments and reveals according to the actual committee member role associated with the signing key, rather than treating all allowed signers through one undifferentiated path.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `availability`

## Short Reusable Lesson

- Aggregation should account for commitments and reveals according to the actual committee member role associated with the signing key, rather than treating all allowed signers through one undifferentiated path. In this pattern, the visible evidence suggests the aggregation logic depended on signer role, but the pre-patch path used a broad membership check and a generic aggregation flow. That likely made role-specific accounting fragile or incorrect under concurrent message handling. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
