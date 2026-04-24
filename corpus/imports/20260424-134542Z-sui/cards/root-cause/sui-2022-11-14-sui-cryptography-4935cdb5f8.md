# Root-Cause Card

## Metadata

- ID: `sui-2022-11-14-sui-cryptography-4935cdb5f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-epoch-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: epoch-scoped certificate material -> signature verifier

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: cross-epoch-replay-risk
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch changes Sui authority signatures from signing only the message value to signing the value plus EpochId, and updates checkpoint fragment verification to supply the current committee epoch.
