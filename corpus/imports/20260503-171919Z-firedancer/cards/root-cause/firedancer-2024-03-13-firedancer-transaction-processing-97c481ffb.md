# Root-Cause Card

## Metadata

- ID: `firedancer-2024-03-13-firedancer-transaction-processing-97c481ffb`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `exact-account-instance-authorization`

## Violated Invariant

- Invariant: A mutation gate must validate writability and privilege on the exact account instance being modified, not on any aliased account with the same address.

## Trust Boundary

- Boundary: Transaction-supplied instruction account metadata crossing into runtime mutation checks.

## Attack Surface

- Entrypoint type: instruction account authorization gate
- Sensitive sink: mutable account access in runtime program execution

## Impact Pattern

- Primary impact: privilege misuse
- Secondary impact: none

## Short Reusable Lesson

- The runtime answered “is this writable?” by searching for any writable alias of the same address instead of checking the exact indexed instruction account being mutated.
