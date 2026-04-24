# Root-Cause Card

## Metadata

- ID: `sui-2023-02-02-sui-cryptography-7ec4bccdd4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-quorum-hardening`
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

- Primary impact: consensus-safety
- Secondary impact: fork-risk-reduction

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch hardens Sui checkpoint certification by replacing `AuthorityWeakQuorumSignInfo` with `AuthorityStrongQuorumSignInfo` for `CertifiedCheckpointSummary` and related aggregation paths. The evidence supports consensus/checkpoint quorum hardening, not signature forgery, replay, nonce misuse, or a fully demonstrated exploit.
