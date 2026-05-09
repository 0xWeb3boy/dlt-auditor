# Root-Cause Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-7395c52e`
- Bug family: `authz_and_role_gates`
- Bug class: `callback-context-access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `callback-context authorization`

## Violated Invariant

- Invariant: A privileged or module-originated callback context must not be allowed to invoke mutable native precompile methods unless that context is explicitly authorized for the method.

## Trust Boundary

- Boundary: Contract callback execution crosses from EVM into native module precompile authority checks.

## Attack Surface

- Entrypoint type: FunToken or Wasm precompile call from VM callback context
- Sensitive sink: mutable native precompile method execution

## Impact Pattern

- Primary impact: callback-context privilege misuse
- Secondary impact: unexpected native state mutation

## Short Reusable Lesson

- Mutable precompile methods added an explicit VM-sender guard so callback-originated execution cannot reach native state-changing logic.
