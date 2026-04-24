# Root-Cause Card

## Metadata

- ID: `sui-2022-12-29-sui-storage-b376f812b5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `epoch-transition-race`
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
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes a concrete race between certificate execution and authority reconfiguration by adding an execution-epoch RwLock, requiring certificate execution to hold a read guard for the matching epoch, and requiring reconfiguration to hold a write guard while reverting uncommitted epoch transactions and advancing epoch.
