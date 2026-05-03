# Root-Cause Card

## Metadata

- ID: `firedancer-2024-10-08-firedancer-storage-3945455a3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `runtime-program-admissibility`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `pre-dispatch-program-admissibility`

## Violated Invariant

- Invariant: A runtime must validate that every candidate program account is executable and admissible before dispatching it.

## Trust Boundary

- Boundary: Transaction-selected program accounts crossing into the executor dispatch path.

## Attack Surface

- Entrypoint type: transaction pre-execution check
- Sensitive sink: program dispatch and execution

## Impact Pattern

- Primary impact: invalid program execution
- Secondary impact: consensus integrity

## Short Reusable Lesson

- The execution path lacked a dedicated admissibility gate and trusted downstream logic to notice invalid program accounts too late.
