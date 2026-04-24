# Root-Cause Card

## Metadata

- ID: `bor-2026-04-16-bor-transaction-processing-11ecb6aa7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic bounds and resource accounting`

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

- The shown issue is an enforcement gap at the Bor finalization boundary: invalid or unsupported conditions were not surfaced as explicit errors from Finalize, and callers had no direct failure channel. The excerpts support missing validation and error propagation; they do not fully prove a deeper corruption or exploit path.
