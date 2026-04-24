# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-8e38834340`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-sync-state`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: While the execution layer is syncing, the node should not advertise or persist the current unsafe payload as safe or finalized unless those checkpoints are actually established, and a closed sync-complete channel must not dominate a biased select! and distort the intended sync gate.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- While the execution layer is syncing, the node should not advertise or persist the current unsafe payload as safe or finalized unless those checkpoints are actually established, and a closed sync-complete channel must not dominate a biased select! and distort the intended sync gate. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
