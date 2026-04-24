# Root-Cause Card

## Metadata

- ID: `sui-2023-03-06-sui-consensus-e4c9e8c80c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unverified-consensus-timestamp-source`
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

- Primary impact: integrity-risk
- Secondary impact: consensus-timestamp-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch likely fixes a security-relevant consensus timestamp-source bug. The consensus handler previously passed `consensus_output.sub_dag.leader.metadata.created_at` into the consensus commit prologue. The commit message states that certificate metadata timestamps are not verified and could lead to security issues.
