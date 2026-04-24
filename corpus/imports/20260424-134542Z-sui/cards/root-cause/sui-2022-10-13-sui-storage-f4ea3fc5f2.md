# Root-Cause Card

## Metadata

- ID: `sui-2022-10-13-sui-storage-f4ea3fc5f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-state-confusion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch addresses a stale-epoch certificate handling bug in Sui authority/node-sync storage. The supplied evidence supports a correctness and state-integrity fix around epoch transitions, but does not establish an exploitable vulnerability or a concrete protocol security failure.
