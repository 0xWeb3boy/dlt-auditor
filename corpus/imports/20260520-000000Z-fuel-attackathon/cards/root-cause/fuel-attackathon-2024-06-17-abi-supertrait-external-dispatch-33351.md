# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-abi-supertrait-external-dispatch-33351`
- Bug family: `authz_and_role_gates`
- Bug class: `supertrait-method-dispatch-exposure`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `external-interface-visibility-enforcement`

## Violated Invariant

- Only functions explicitly exposed by a contract ABI may be reachable through external contract dispatch.

## Trust Boundary

- Boundary: `external-call->contract-dispatch-table`
- Entrypoint type: `contract-call-dispatch`
- Sensitive sink: `execution of ABI supertrait helper methods that developers expected to be internal`

## Attack Surface

- Call a contract selector corresponding to a supertrait method.
- Choose calldata for methods omitted from the generated ABI.

## Exploit Preconditions

- Compiler omits supertrait methods from ABI JSON but still leaves them reachable in dispatch IR.
- The supertrait method performs privileged work without its own access control.

## Impact Pattern

- Primary impact: `unauthorized-action`
- Secondary impact: `access-control-bypass`
- Blast radius: `ecosystem-wide`
- Severity guess: `critical`

## Short Reusable Lesson

- Visibility rules must be enforced at every externally reachable dispatch surface, not only in generated metadata.
