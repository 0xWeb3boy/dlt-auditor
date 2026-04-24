# Root-Cause Card

## Metadata

- ID: `sui-2022-08-26-sui-cryptography-3278bff6e3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-error-misclassification`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: consensus-liveness
- Secondary impact: state-integrity

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes security-relevant error misclassification in the Narwhal consensus handling path. The prior design used broad SuiError/FragmentInternalError classification to decide whether consensus execution should continue or stop.
