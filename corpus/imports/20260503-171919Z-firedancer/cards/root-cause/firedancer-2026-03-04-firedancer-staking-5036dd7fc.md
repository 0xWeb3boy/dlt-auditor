# Root-Cause Card

## Metadata

- ID: `firedancer-2026-03-04-firedancer-staking-5036dd7fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bounds-check-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-index-capacity-validation`

## Violated Invariant

- Invariant: Consensus-sensitive reward arrays must validate delegation indexes against capacity before indexing fixed result buffers.

## Trust Boundary

- Boundary: Stake-delegation metadata crossing into reward distribution arrays.

## Attack Surface

- Entrypoint type: reward-calculation path
- Sensitive sink: stake result array indexing

## Impact Pattern

- Primary impact: memory safety
- Secondary impact: none

## Short Reusable Lesson

- Reward code indexed a fixed result array directly from delegation metadata even when capacity-derived indexes could exceed the expected range.
