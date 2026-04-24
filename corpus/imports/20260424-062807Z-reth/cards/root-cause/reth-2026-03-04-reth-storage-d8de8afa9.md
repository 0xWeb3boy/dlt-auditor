# Root-Cause Card

## Metadata

- ID: `reth-2026-03-04-reth-storage-d8de8afa9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-invariant-enforcement`

## Violated Invariant

- Invariant: Account and storage hashing stages should preserve the intended hashed-state result while selecting a mode that keeps memory use bounded across the full remaining catch-up range, not just the next scheduled batch.

## Trust Boundary

- Boundary: large state range -> hashing stage resource planner

## Attack Surface

- Entrypoint type: database-stage-runner
- Sensitive sink: memory budget and stage progress

## Impact Pattern

- Primary impact: availability
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Account and storage hashing stages should preserve the intended hashed-state result while selecting a mode that keeps memory use bounded across the full remaining catch-up range, not just the next scheduled batch.
