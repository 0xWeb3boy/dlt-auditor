# Root-Cause Card

## Metadata

- ID: `bor-2020-05-13-bor-cryptography-0f8d3b100`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-boundary-validation`
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

- The verifier used data from different points in the sprint transition: it built expected validator bytes from a snapshot rooted at number-1 but previously compared them to the current header's Extra bytes instead of the parent sprint-boundary header that corresponds to that snapshot.
