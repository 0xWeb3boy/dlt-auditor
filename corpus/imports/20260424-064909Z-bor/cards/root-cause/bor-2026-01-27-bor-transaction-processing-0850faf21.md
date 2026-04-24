# Root-Cause Card

## Metadata

- ID: `bor-2026-01-27-bor-transaction-processing-0850faf21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-invariant-checks`
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

- Primary impact: consensus-integrity-risk
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The evidenced root cause is missing validation of internal consensus-related invariants at sensitive boundaries, especially after Bor finalization and before root-hash or rewind decisions.
