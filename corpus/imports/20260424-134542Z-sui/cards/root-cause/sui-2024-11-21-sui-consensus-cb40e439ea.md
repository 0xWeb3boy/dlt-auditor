# Root-Cause Card

## Metadata

- ID: `sui-2024-11-21-sui-consensus-cb40e439ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-limit-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: invalid-block-production
- Secondary impact: consensus-liveness-risk

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes a consensus block-construction accounting bug. The transaction consumer now checks aggregate block bytes and selected-plus-incoming transaction count before accepting a transaction batch, aligning proposal behavior with verifier-side protocol limits.
