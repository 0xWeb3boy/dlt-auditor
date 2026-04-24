# Root-Cause Card

## Metadata

- ID: `optimism-2025-06-02-optimism-rpc-client-api-09dfe35bc5`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Access-list approval should use the correct executing-chain context and should only pass for execution times that satisfy the validator's ordering and expiry rules; same-timestamp execution is not considered safely verifiable in this check path.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: policy-bypass-risk
- Secondary impact: authorization-or-policy-bypass

## Short Reusable Lesson

- Access-list approval should use the correct executing-chain context and should only pass for execution times that satisfy the validator's ordering and expiry rules; same-timestamp execution is not considered safely verifiable in this check path. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce authorization at the boundary and fail closed before state, privilege, or consensus-visible output changes.
