# Root-Cause Card

## Metadata

- ID: `bor-2023-03-21-bor-storage-d53c1ec21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-verification`
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

- The verifier's validator lookup logic mixed consensus checking with fallback retry behavior that could change the state source from the immediate parent context to older ancestors after errors, instead of using one explicit lookup path.
