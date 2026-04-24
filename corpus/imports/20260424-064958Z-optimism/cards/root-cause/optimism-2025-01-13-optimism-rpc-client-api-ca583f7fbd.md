# Root-Cause Card

## Metadata

- ID: `optimism-2025-01-13-optimism-rpc-client-api-ca583f7fbd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-context-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: In interop mode, L2 data lookups and proof checks should be bound to the intended chain and requested block context, not inferred from an ambient default chain or unrelated head block.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- In interop mode, L2 data lookups and proof checks should be bound to the intended chain and requested block context, not inferred from an ambient default chain or unrelated head block. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce domain-separation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
