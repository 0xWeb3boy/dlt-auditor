# Root-Cause Card

## Metadata

- ID: `optimism-2022-09-19-optimism-storage-af3e56b124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-invariant-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: The L2OutputOracle's owner and proposer should not be the same address on initialization or after later administrative changes.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: authorization-policy-bypass
- Secondary impact: state-integrity

## Short Reusable Lesson

- The L2OutputOracle's owner and proposer should not be the same address on initialization or after later administrative changes. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce authorization at the boundary and fail closed before state, privilege, or consensus-visible output changes.
