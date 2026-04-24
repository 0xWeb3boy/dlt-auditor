# Root-Cause Card

## Metadata

- ID: `sui-2022-06-24-sui-transaction-processing-8a3d0789ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-execution-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds explicit checkpoint/execution consistency checks in Sui checkpointing code, rejecting checkpoint contents that include unexecuted transactions.
