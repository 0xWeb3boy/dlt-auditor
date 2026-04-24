# Root-Cause Card

## Metadata

- ID: `bor-2024-04-30-bor-cryptography-bd8fe6260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `operand-decoding-error`
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

- Primary impact: incorrect-authorized-call-execution
- Secondary impact: low severity conditions

## Short Reusable Lesson

- opAuthCall consumed one more stack item than the subsequent logic used, so later operands could be shifted relative to the intended AUTHCALL layout.
