# Root-Cause Card

## Metadata

- ID: `optimism-2023-05-04-optimism-rpc-client-api-73f310c0e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: In a consensus-aware proxyd backend group, RPC requests that reference chain state by block tag or block number should be rewritten or rejected against the group's tracked consensus block, rather than forwarded unchanged to a backend.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: client-view-divergence

## Short Reusable Lesson

- In a consensus-aware proxyd backend group, RPC requests that reference chain state by block tag or block number should be rewritten or rejected against the group's tracked consensus block, rather than forwarded unchanged to a backend. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
