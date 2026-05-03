# Root-Cause Card

## Metadata

- ID: `firedancer-2025-03-05-firedancer-consensus-97c08c390`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-bound-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `counter-clamping-before-exponentiation`

## Violated Invariant

- Invariant: State-derived counters must be clamped to protocol bounds before powering, shifting, or indexing with them.

## Trust Boundary

- Boundary: Vote-state confirmation counts crossing into lockout math.

## Attack Surface

- Entrypoint type: vote-state processing
- Sensitive sink: lockout exponentiation and duration calculation

## Impact Pattern

- Primary impact: consensus hardening
- Secondary impact: none

## Short Reusable Lesson

- Consensus math fed a confirmation counter into power-of-two logic before proving it was within the protocol’s lockout history bound.
