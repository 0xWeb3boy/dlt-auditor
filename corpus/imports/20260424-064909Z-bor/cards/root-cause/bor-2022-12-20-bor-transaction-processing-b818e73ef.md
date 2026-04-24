# Root-Cause Card

## Metadata

- ID: `bor-2022-12-20-bor-transaction-processing-b818e73ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_a_confirmed`

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
- Secondary impact: high severity conditions

## Short Reusable Lesson

- Beacon.VerifyHeaders relied too much on caller-side sanitization and caller-prepared auxiliary state when validating mixed pre-/post-merge header batches.
