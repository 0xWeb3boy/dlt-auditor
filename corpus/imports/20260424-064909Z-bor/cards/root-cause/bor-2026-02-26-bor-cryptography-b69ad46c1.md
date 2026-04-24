# Root-Cause Card

## Metadata

- ID: `bor-2026-02-26-bor-cryptography-b69ad46c1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `timestamp-validation`
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

- Primary impact: availability
- Secondary impact: denial-of-service

## Short Reusable Lesson

- After Rio relaxed timestamp validation to allow flexible block times, verifyHeader no longer enforced an upper bound on validator-controlled header.Time relative to the local clock.
