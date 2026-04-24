# Root-Cause Card

## Metadata

- ID: `sui-2022-07-23-sui-cryptography-87d5950c06`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-type-registration-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: signature-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch centralizes and seals BcsSignable registration for types that use BCS-based signing helpers. This is security-adjacent hardening of a sensitive signing serialization boundary, but the provided evidence does not establish a concrete vulnerability, exploit path, or prior unsafe behavior beyond distributed trait.
