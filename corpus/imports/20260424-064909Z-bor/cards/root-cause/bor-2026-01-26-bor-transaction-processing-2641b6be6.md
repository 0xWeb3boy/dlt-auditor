# Root-Cause Card

## Metadata

- ID: `bor-2026-01-26-bor-transaction-processing-2641b6be6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: consensus-failure
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- State-sync finalization under-enforced the block validity invariant: the code path shown did not prove that the block body's trailing state-sync transaction matched the locally derived state-sync payload, and downstream processing did not immediately fail on the resulting receipt/transaction mismatch.
