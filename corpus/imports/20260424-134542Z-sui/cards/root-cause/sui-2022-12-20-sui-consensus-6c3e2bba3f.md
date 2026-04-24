# Root-Cause Card

## Metadata

- ID: `sui-2022-12-20-sui-consensus-6c3e2bba3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-epoch-invariant-hardening`
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

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The evidence supports a consensus/reconfiguration correctness hardening: the patch carries an intended epoch into transaction-processing paths and adds checked loading of the per-epoch store. It does not establish a vulnerability, attacker influence, exploitability, consensus fork, asset loss, or other concrete security impact.
