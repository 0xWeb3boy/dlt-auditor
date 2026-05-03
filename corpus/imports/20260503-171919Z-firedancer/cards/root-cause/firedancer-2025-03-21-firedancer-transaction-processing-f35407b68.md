# Root-Cause Card

## Metadata

- ID: `firedancer-2025-03-21-firedancer-transaction-processing-f35407b68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `memory-lifetime`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `lifetime-safe-owned-metadata-storage`

## Violated Invariant

- Invariant: Metadata referenced across nested execution must live in storage owned by the transaction or call context, not a transient stack frame.

## Trust Boundary

- Boundary: Caller-controlled nested execution state crossing from setup code into later CPI use.

## Attack Surface

- Entrypoint type: nested call / CPI setup path
- Sensitive sink: instruction-info pointer dereference after scope exit

## Impact Pattern

- Primary impact: memory safety
- Secondary impact: none

## Short Reusable Lesson

- The runtime stored CPI instruction metadata in a stack-local object even though later execution paths continued using it after the setup frame returned.
