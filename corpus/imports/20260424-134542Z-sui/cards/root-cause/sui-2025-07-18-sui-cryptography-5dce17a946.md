# Root-Cause Card

## Metadata

- ID: `sui-2025-07-18-sui-cryptography-5dce17a946`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-commitment-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds an `IndirectStateObserver` and conditionally folds observed indirect state into the additional consensus digest recorded in the consensus commit prologue.
