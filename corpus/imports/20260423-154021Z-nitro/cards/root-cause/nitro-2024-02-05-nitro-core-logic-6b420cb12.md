# Root-Cause Card

## Metadata

- ID: `nitro-2024-02-05-nitro-core-logic-6b420cb12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-state-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `challenged-state-gating`

## Violated Invariant

- Invariant: A confirmation or finalize action should re-check whether the target object is challenged or otherwise blocked before submitting the side effect.

## Trust Boundary

- Boundary: `local challenge state->assertion confirmation path`

## Attack Surface

- Entrypoint type: `confirmation-or-finalization`
- Sensitive sink: `confirming an assertion or similar finalizing action`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- A confirmation or finalize action should re-check whether the target object is challenged or otherwise blocked before submitting the side effect. The supported finding is a business-logic guard addition: the patch teaches the assertion confirmation flow to stop when the target assertion is locally known to be challenged. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
