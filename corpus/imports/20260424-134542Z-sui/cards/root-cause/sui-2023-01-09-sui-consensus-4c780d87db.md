# Root-Cause Card

## Metadata

- ID: `sui-2023-01-09-sui-consensus-4c780d87db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-rollback`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: finality-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes an epoch-transition ordering bug where local rollback could revert a transaction that had already been executed through checkpoint processing. The evidence supports a consensus/finality integrity issue, but does not prove a remote exploit path, asset theft, signature bypass, or permanent chain-wide fork.
