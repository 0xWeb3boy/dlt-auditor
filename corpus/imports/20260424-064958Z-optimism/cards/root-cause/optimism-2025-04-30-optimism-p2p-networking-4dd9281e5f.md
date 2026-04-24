# Root-Cause Card

## Metadata

- ID: `optimism-2025-04-30-optimism-p2p-networking-4dd9281e5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-identity-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: A node's configured libp2p keypair, ENR-derived PeerId, and discovery behavior should stay consistent with each other instead of silently changing at runtime.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: peer-identity-inconsistency
- Secondary impact: discovery-misconfiguration

## Short Reusable Lesson

- A node's configured libp2p keypair, ENR-derived PeerId, and discovery behavior should stay consistent with each other instead of silently changing at runtime. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
