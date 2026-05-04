# Root-Cause Card

## Metadata

- ID: `fuel-core-2025-04-17-fuel-core-storage-103c019fa1`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `missing-utxo-consumption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Every successfully spent spendable input variant must be removed or marked consumed atomically with transaction execution.

## Trust Boundary

- Boundary: `transaction-input->utxo-storage`
- Entrypoint type: `state-transition`
- Sensitive sink: `UTXO spend set and persistent coin storage`

## Attack Surface

- Submit transactions spending data coin inputs.
- Attempt a second transaction spending the same data coin after the first commit.

## Exploit Preconditions

- Data coin input variants are valid spendable inputs.
- The spend-pruning match omits those variants while other execution paths accept them.

## Impact Pattern

- Primary impact: `double-spend`
- Secondary impact: `state-integrity`
- Blast radius: `chain-wide`
- Severity guess: `critical`

## Short Reusable Lesson

- Variant-rich state machines need exhaustive consumption logic for every accepted spendable input type.
