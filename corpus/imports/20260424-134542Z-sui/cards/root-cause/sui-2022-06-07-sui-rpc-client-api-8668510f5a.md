# Root-Cause Card

## Metadata

- ID: `sui-2022-06-07-sui-rpc-client-api-8668510f5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-integrity-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: remote client/proxy request or response -> node API trust decision

## Attack Surface

- Entrypoint type: rpc-handler
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch changes Sui checkpoint handling by adding a previous checkpoint digest to checkpoint summary/proposal construction paths and by comparing fetched checkpoint contents against content_digest instead of the whole checkpoint digest.
