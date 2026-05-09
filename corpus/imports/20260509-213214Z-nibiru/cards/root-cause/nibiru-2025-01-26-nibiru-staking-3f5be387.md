# Root-Cause Card

## Metadata

- ID: `nibiru-2025-01-26-nibiru-staking-3f5be387`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-runtime-state-sync`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cross-runtime balance synchronization`

## Violated Invariant

- Invariant: When native module operations move balances visible to another runtime, both runtimes must observe the same balances before execution continues.

## Trust Boundary

- Boundary: EVM contract execution crosses through a Wasm/native staking precompile into bank module account transfers.

## Attack Surface

- Entrypoint type: EVM-to-Wasm staking flow that delegates coins to a module account
- Sensitive sink: EVM StateDB account cache for sender and module account balances

## Impact Pattern

- Primary impact: cross-runtime stale balance
- Secondary impact: dirty-state accounting risk

## Short Reusable Lesson

- A native bank delegation wrapper now synchronizes EVM-visible account state for both sender and recipient module accounts after EVM-denom balance movement.
