# Root-Cause Card

## Metadata

- ID: `bor-2022-10-13-bor-consensus-b70723d70`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-chain-validation`
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

- Primary impact: chain-validation-risk
- Secondary impact: low severity conditions

## Short Reusable Lesson

- The evidence points to incomplete milestone lock-state handling: the prior code did not fully enforce monotonic lock transitions and did not retain the associated end-block hash in the lock state.
