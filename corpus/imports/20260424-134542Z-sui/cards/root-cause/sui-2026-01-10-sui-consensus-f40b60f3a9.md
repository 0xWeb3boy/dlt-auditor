# Root-Cause Card

## Metadata

- ID: `sui-2026-01-10-sui-consensus-f40b60f3a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-finalization-hardening`
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

- Primary impact: consensus-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch changes consensus finalization logic so transactions in blocks below the leader-derived GC bound are not directly finalized based only on commit evidence.
