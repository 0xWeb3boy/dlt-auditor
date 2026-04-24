# Root-Cause Card

## Metadata

- ID: `bor-2017-05-12-bor-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `chain-config-validation`
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

- ChainConfig.checkCompatible enforced historical compatibility for several fork parameters but omitted MetropolisBlock, leaving that fork point out of the existing compatibility gate.
