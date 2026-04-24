# Root-Cause Card

## Metadata

- ID: `bor-2025-04-08-bor-transaction-processing-2e739fce5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: availability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The txpool did not fully enforce cross-subpool exclusivity for delegated senders and SetCode authority addresses. From the supplied evidence, that left room for blob and authorization-related transactions to interact in a way that could be used to create txpool eviction and cancellation pressure.
