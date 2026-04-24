# Root-Cause Card

## Metadata

- ID: `bor-2026-02-17-bor-cryptography-d9fac7a4c`
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

- Primary impact: correctness-or-hardening
- Secondary impact: low severity conditions

## Short Reusable Lesson

- Validation logic relied on implicit or narrower checks instead of explicit structural validation. In the clearest case, consensus code used a Uint64() comparison for block-number continuity rather than full-precision arithmetic; adjacent changes likewise add explicit malformed-input checks that were previously assumed away.
