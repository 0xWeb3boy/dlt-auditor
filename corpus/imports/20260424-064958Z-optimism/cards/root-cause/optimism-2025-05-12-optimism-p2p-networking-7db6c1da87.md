# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-12-optimism-p2p-networking-7db6c1da87`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-machine-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: Derivation startup should begin from a coherent L2 forkchoice state, and safe-head updates should only be treated as consumed according to explicit change/acknowledgement semantics rather than a loose block-number comparison.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: node-desync
- Secondary impact: node-stall

## Short Reusable Lesson

- Derivation startup should begin from a coherent L2 forkchoice state, and safe-head updates should only be treated as consumed according to explicit change/acknowledgement semantics rather than a loose block-number comparison. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
