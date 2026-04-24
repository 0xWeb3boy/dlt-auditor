# Root-Cause Card

## Metadata

- ID: `bor-2021-09-13-bor-transaction-processing-b8d7c662c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trace-output-exposure-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input validation and invariant enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: trace-data-exposure
- Secondary impact: low severity conditions

## Short Reusable Lesson

- The trace configuration used permissive default semantics for verbose fields by expressing them as disable-flags, so zero-value/default behavior included memory and return data unless callers turned them off.
