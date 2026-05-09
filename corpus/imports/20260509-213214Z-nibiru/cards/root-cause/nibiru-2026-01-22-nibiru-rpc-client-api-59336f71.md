# Root-Cause Card

## Metadata

- ID: `nibiru-2026-01-22-nibiru-rpc-client-api-59336f71`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `deterministic iteration order`

## Violated Invariant

- Invariant: Consensus-visible state updates and event outputs must be derived from deterministic iteration over collections on every validator.

## Trust Boundary

- Boundary: In-memory map aggregation crosses into consensus state updates, reward distribution, and block-result events.

## Attack Surface

- Entrypoint type: oracle end-block or keeper reward/update path
- Sensitive sink: validator miss counters, reward distribution, and emitted validator performance events

## Impact Pattern

- Primary impact: consensus state divergence
- Secondary impact: chain halt or fork risk

## Short Reusable Lesson

- Consensus logic ranged over a Go map while updating oracle validator state and rewards; the fix canonicalized validator address order before all consensus-visible effects.
