# Root-Cause Card

## Metadata

- ID: `sui-2022-05-18-sui-cryptography-ca9984cda2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-validation`
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

- Primary impact: consensus-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The evidence supports a security-hardening classification for shared-object consensus input validation. The patch adds a local certificate.contains_shared_object() guard before shared-object consensus handling continues.
