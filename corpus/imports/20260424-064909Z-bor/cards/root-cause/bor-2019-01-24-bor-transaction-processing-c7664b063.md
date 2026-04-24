# Root-Cause Card

## Metadata

- ID: `bor-2019-01-24-bor-transaction-processing-c7664b063`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-hardening`
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

- Primary impact: consensus-divergence
- Secondary impact: unsafe-execution-semantics

## Short Reusable Lesson

- The shown code lacked first-class handling for the Petersburg/ConstantinopleFix fork. The evidence supports missing protocol-update support across consensus-critical paths, not a clearly demonstrated local implementation flaw with a proven exploit path.
