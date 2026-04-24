# Root-Cause Card

## Metadata

- ID: `sui-2025-11-26-sui-consensus-3b59b5be60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: committing fees, balances, or resource accounting state

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is a consensus vote-accounting fix for Mysticeti fastpath finalization under garbage collection. It adds a guard that skips counting votes from a block when a same-author origin ancestor above the pending block round is missing from the retained block map and may have been GC'ed.
