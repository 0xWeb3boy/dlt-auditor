# Root-Cause Card

## Metadata

- ID: `avalanchego-2026-03-25-avalanchego-staking-fc749bb8c1`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-validator-weight-arithmetic`

## Violated Invariant

- Invariant: Validator weight and reward-derived accounting values must be checked for representability before they are installed into consensus or staking state.

## Trust Boundary

- Boundary: Persisted staking metadata and validator transactions cross into in-memory validator set reconstruction.

## Attack Surface

- Entrypoint type: PlatformVM current validator state loading
- Sensitive sink: effective validator weight used for staking/accounting state

## Impact Pattern

- Primary impact: consensus-state-integrity, validator-accounting-integrity
- Secondary impact: medium_high_integrity

## Root Cause

- The grounded root cause is unchecked integer arithmetic in the state-loading path for current auto-renewed validators. The previous code did not enforce that original validator weight plus accrued validator rewards plus accrued delegatee rewards fit in uint64 before using the derived weight. ## Walkthrough 1.

## Short Reusable Lesson

- Auto-renewed validator weight reconstruction changed from unchecked uint64 addition to checked safemath additions. The reusable shape is persisted accounting state reconstructed by summing bounded integer fields before use in validator power or reward logic.
