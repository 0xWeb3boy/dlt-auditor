# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-call-frame-code-size-address-33451`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `call-frame-field-dereference-error`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `semantic-field-binding`

## Violated Invariant

- A call-frame accessor documented to return a field value must load that value, not return the field's memory address.

## Trust Boundary

- Boundary: `contract-introspection->authorization-or-policy-check`
- Entrypoint type: `library-function`
- Sensitive sink: `code-size based security policy`

## Attack Surface

- Call or deploy a contract whose real code size should fail a policy check.
- Rely on code_size returning a safe-looking address instead of size.

## Exploit Preconditions

- code_size returns the memory offset of the call-frame field.
- A contract uses code_size to gate access, swaps, or interactions.

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `unauthorized-action`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Introspection APIs used in policy checks must be tested against semantic values, not just non-zero outputs.
