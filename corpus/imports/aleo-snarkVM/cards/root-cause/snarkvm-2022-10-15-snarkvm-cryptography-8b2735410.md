# Root-Cause Card

## Metadata

- ID: `snarkvm-2022-10-15-snarkvm-cryptography-8b2735410`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-consensus-target-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-target-validation`

## Violated Invariant

- Invariant: Proof-of-work or coinbase puzzle verification must bind the active target thresholds at every admission point that accepts prover or coinbase solutions.

## Trust Boundary

- Boundary: prover-supplied puzzle solution -> consensus verification

## Attack Surface

- Entrypoint type: block-or-mempool-validation
- Sensitive sink: coinbase/prover solution acceptance and reward eligibility

## Impact Pattern

- Primary impact: consensus validation hardening
- Secondary impact: reward accounting integrity

## Short Reusable Lesson

- Consensus-critical difficulty thresholds should be explicit verifier inputs, not implicit assumptions at scattered call sites.
