# Root-Cause Card

## Metadata

- ID: `optimism-2025-02-18-optimism-rpc-client-api-6e39803ab8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-config-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: If interop consolidation is security-relevant, all participants should evaluate it against the same DependencySet sourced from boot configuration rather than rebuilding an equivalent-looking set locally from parallel inputs.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: state-integrity

## Short Reusable Lesson

- If interop consolidation is security-relevant, all participants should evaluate it against the same DependencySet sourced from boot configuration rather than rebuilding an equivalent-looking set locally from parallel inputs. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
