# Root-Cause Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-core-logic-fd99d9175`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `definite-initialization-before-helper-use`

## Violated Invariant

- Invariant: Guard or borrow wrappers passed into helper macros must be fully initialized before any helper reads their fields.

## Trust Boundary

- Boundary: Runtime account metadata crossing into helper macros that borrow or validate account state.

## Attack Surface

- Entrypoint type: account-borrow helper setup
- Sensitive sink: guarded borrow helper macros

## Impact Pattern

- Primary impact: correctness or hardening
- Secondary impact: none

## Short Reusable Lesson

- Stack-local borrowed-account wrappers were passed to helper macros without deterministic zero-initialization, leaving helper behavior dependent on stale stack bytes.
