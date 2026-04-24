# Root-Cause Card

## Metadata

- ID: `bor-2015-01-13-bor-transaction-processing-82beaabf6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-mismatch`
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

- Consensus-sensitive logic was encoded with brittle local control flow and an incorrect rule constant: the CREATE code-deposit check reused an enclosing error variable, and uncle processing used a different ancestor depth than the fixed code.
