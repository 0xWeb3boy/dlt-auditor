# Root-Cause Card

## Metadata

- ID: `sui-2022-07-15-sui-cryptography-da264c340e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-response-verification`
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

- Primary impact: checkpoint-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best classified as checkpoint response verification hardening. It adds centralized `CheckpointResponse::verify(&Committee)` and calls it before request-specific validation in the safe client, and it adds a guard for missing requested detail on signed or certified past checkpoints.
