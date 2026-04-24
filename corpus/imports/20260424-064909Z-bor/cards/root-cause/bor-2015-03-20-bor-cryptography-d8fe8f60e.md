# Root-Cause Card

## Metadata

- ID: `bor-2015-03-20-bor-cryptography-d8fe8f60e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input validation and invariant enforcement`

## Violated Invariant

- Invariant: Untrusted inputs must be checked against the protocol invariant before they can reach a state-changing or security-sensitive sink.

## Trust Boundary

- Boundary: untrusted protocol input to trusted node logic boundary

## Attack Surface

- Entrypoint type: validation or decoding path
- Sensitive sink: state mutation or security-relevant decision

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: low severity conditions

## Short Reusable Lesson

- Critical Ethash helper routines depended on assertion-only checks for bounds and alignment instead of explicit runtime validation and error propagation.
