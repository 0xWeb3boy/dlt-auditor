# Root-Cause Card

## Metadata

- ID: `bor-2014-11-12-bor-transaction-processing-60cdb1148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-omission`
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

- Primary impact: integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The code had an omitted transaction-root validation step in block processing and non-canonical handling of empty trie roots in GetRoot(), which could lead to inconsistent commitment checking behavior.
