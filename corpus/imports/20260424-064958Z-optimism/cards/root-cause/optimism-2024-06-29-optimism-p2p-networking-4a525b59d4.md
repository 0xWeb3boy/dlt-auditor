# Root-Cause Card

## Metadata

- ID: `optimism-2024-06-29-optimism-p2p-networking-4a525b59d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-selection-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When the optional p2p.sync.onlyreqtostatic policy is enabled, outbound req/resp sync requests should be initiated only for static peers.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: reduced-attack-surface
- Secondary impact: security-hardening-or-correctness

## Short Reusable Lesson

- When the optional p2p.sync.onlyreqtostatic policy is enabled, outbound req/resp sync requests should be initiated only for static peers. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
