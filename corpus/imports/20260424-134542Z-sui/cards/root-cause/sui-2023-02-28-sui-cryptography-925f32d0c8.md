# Root-Cause Card

## Metadata

- ID: `sui-2023-02-28-sui-cryptography-925f32d0c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-metadata-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: consensus-configuration-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds centralized validator metadata verification before active validator metadata is used to construct Narwhal committee and worker-cache configuration.
