# Root-Cause Card

## Metadata

- ID: `bor-2022-06-29-bor-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-validation`
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

- The transition-validation path did not visibly enforce the terminal-total-difficulty invariant on the pre-merge PoW segment before asynchronous result aggregation, and the collector could overwrite an earlier TTD-based rejection. That left the terminal-block validity rule under-enforced in the mixed merge-transition path.
