# Root-Cause Card

## Metadata

- ID: `optimism-2024-11-27-optimism-rpc-client-api-c8f4b3a0e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `security-sensitive-config-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: Deployment intents should be normalized and validated against standard-chain expectations before the apply pipeline runs, so malformed or inconsistent role and artifact/version inputs fail early.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: unsafe-deployment-configuration
- Secondary impact: privileged-role-misconfiguration

## Short Reusable Lesson

- Deployment intents should be normalized and validated against standard-chain expectations before the apply pipeline runs, so malformed or inconsistent role and artifact/version inputs fail early. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
