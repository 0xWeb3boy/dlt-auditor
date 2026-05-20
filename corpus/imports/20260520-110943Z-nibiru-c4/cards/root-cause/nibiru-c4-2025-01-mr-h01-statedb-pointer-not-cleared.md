# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h01-statedb-pointer-not-cleared`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `statedb-pointer-lifecycle-cleanup-missing`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state pointer lifecycle cleanup`

## Violated Invariant

- Invariant: A transaction-scoped StateDB pointer must be cleared after EVM/precompile execution so later read-only or bank paths cannot observe stale transaction state.

## Trust Boundary

- Boundary: EVM/precompile execution->shared bank keeper field

## Attack Surface

- Entrypoint type: FunToken or Wasm precompile execution
- Sensitive sink: NibiruBankKeeper.StateDB pointer used by SyncStateDBWithAccount

## Impact Pattern

- Primary impact: stale StateDB pointer persists past transaction scope
- Secondary impact: consensus nondeterminism regression

## Short Reusable Lesson

- A post-contest mitigation still assigned the bank StateDB pointer in precompile paths but did not reliably clear it back to nil after execution.
