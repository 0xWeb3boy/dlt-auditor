# Root-Cause Card

## Metadata

- ID: `bor-2026-04-13-bor-transaction-processing-bc8857fc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`
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

- The finalization interface did not provide an explicit error channel for invalid Bor finalization outcomes, so unsupported block-body fields and some state-sync receipt inconsistencies were represented indirectly through the returned receipts instead of being authoritative failures at the finalization boundary.
