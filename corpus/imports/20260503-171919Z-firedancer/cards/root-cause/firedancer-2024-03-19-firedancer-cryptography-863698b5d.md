# Root-Cause Card

## Metadata

- ID: `firedancer-2024-03-19-firedancer-cryptography-863698b5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-failure`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `tick-state-transition-validation`

## Violated Invariant

- Invariant: Leader-transition and skipped-slot handling must preserve monotonic PoH tick state so replay sees completed blocks with the correct tick history.

## Trust Boundary

- Boundary: Consensus/replay state transitioning from skipped slots into leader production.

## Attack Surface

- Entrypoint type: leader transition / replay state update
- Sensitive sink: tick-height tracking and fork/complete-block decisions

## Impact Pattern

- Primary impact: consensus liveness
- Secondary impact: none

## Short Reusable Lesson

- Replay state failed to carry enough skipped-slot tick information into the first leader slot, leaving later completeness checks with stale tick context.
