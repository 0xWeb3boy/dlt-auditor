# Root-Cause Card

## Metadata

- ID: `optimism-2025-04-24-optimism-p2p-networking-e6b7214cb0`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `trusted-signer-resolution`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-and-context-binding`

## Violated Invariant

- Invariant: If the node relies on an "unsafe block signer" for trust decisions, that signer should come from a canonical runtime source and failures to load or decode the needed metadata should not be silently ignored.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: configuration-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- If the node relies on an "unsafe block signer" for trust decisions, that signer should come from a canonical runtime source and failures to load or decode the needed metadata should not be silently ignored. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce signer-and-context-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
