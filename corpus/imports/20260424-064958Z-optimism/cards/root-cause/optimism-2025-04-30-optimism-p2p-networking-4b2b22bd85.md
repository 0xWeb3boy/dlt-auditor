# Root-Cause Card

## Metadata

- ID: `optimism-2025-04-30-optimism-p2p-networking-4b2b22bd85`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-identity-configuration-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-validation`

## Violated Invariant

- Invariant: A node's libp2p identity, discovery record, and advertised address policy should come from explicit configuration and remain internally consistent rather than being silently rewritten or substituted by fallback behavior.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: identity-consistency
- Secondary impact: misconfiguration-risk-reduction

## Short Reusable Lesson

- A node's libp2p identity, discovery record, and advertised address policy should come from explicit configuration and remain internally consistent rather than being silently rewritten or substituted by fallback behavior. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce configuration-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
