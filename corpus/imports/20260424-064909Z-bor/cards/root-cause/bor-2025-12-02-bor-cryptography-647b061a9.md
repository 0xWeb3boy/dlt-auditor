# Root-Cause Card

## Metadata

- ID: `bor-2025-12-02-bor-cryptography-647b061a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Untrusted inputs must be checked against the protocol invariant before they can reach a state-changing or security-sensitive sink.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: malformed-input-acceptance
- Secondary impact: low severity conditions

## Short Reusable Lesson

- Validation of a consensus-significant field was inconsistent across layers: header sanity permitted wider Difficulty values than the consensus path actually intended to support, and seal verification narrowed the value to uint64 without first enforcing representability.
