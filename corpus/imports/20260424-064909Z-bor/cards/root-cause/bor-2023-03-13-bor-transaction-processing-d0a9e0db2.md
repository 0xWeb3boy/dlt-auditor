# Root-Cause Card

## Metadata

- ID: `bor-2023-03-13-bor-transaction-processing-d0a9e0db2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validator-verification`
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

- Primary impact: consensus-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The validator-set verification logic was tied to the wrong sprint-boundary condition, so the intended check was not performed at the end-of-sprint transition point indicated by the commit. In the same path, validator retrieval/parsing errors were handled with panic(err) rather than normal error propagation, making the verification path brittle.
