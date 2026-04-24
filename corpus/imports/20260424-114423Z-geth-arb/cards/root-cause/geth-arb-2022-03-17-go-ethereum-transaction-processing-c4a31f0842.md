# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-03-17-go-ethereum-transaction-processing-c4a31f0842`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `validator-reorg-state-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-chain-progress-binding`

## Violated Invariant

- Invariant: Validator progress must be bound to the canonical block hash, not only height, so same-height reorgs invalidate stale validation state before further actions are generated.

## Trust Boundary

- Boundary: canonical chain updates -> persisted validator progress

## Attack Surface

- Entrypoint type: validator reorg recovery or progress loader
- Sensitive sink: validator progress continuation and L1 node-action generation

## Impact Pattern

- Primary impact: validator-integrity
- Secondary impact: reorg-safety
- Severity guide: medium

## Short Reusable Lesson

- Validator state tracked the last validated height without sufficiently binding it to the block hash, allowing stale progress to survive an L2 reorg at the same height. Persist and compare the validated block hash with live canonical state, and stop progress when the stored hash mismatches.
