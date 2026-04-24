# Root-Cause Card

## Metadata

- ID: `sui-2022-12-21-sui-consensus-bd9fbd18d3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-boundary-reconfiguration-race`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: consensus-invariant-hardening
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch makes Sui validator certificate handling acquire and check the per-epoch reconfiguration read lock earlier, before certificate verification and later pending-consensus storage.
