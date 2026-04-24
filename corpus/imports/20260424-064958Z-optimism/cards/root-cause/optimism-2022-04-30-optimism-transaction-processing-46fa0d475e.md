# Root-Cause Card

## Metadata

- ID: `optimism-2022-04-30-optimism-transaction-processing-46fa0d475e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-message-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: If unsafe L2 blocks are accepted from gossip, the intake path should be rollup-aware and have the chain- and signer-specific context needed to distinguish valid network messages from unrelated input before forwarding blocks into node processing.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: network-message-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- If unsafe L2 blocks are accepted from gossip, the intake path should be rollup-aware and have the chain- and signer-specific context needed to distinguish valid network messages from unrelated input before forwarding blocks into node processing. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
