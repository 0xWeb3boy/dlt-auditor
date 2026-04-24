# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-efbdcb76b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-transition`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: Forkchoice metadata should not mark an unsafe payload as safe or finalized before execution-layer sync has reached the phase where those labels are justified, and derivation startup signals should not preempt normal event handling merely because a completion channel stays ready.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Forkchoice metadata should not mark an unsafe payload as safe or finalized before execution-layer sync has reached the phase where those labels are justified, and derivation startup signals should not preempt normal event handling merely because a completion channel stays ready. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
