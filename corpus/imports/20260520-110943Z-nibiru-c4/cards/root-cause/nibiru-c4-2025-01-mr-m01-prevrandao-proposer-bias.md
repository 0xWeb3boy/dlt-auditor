# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m01-prevrandao-proposer-bias`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `proposer-biased-randomness-source`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `unbiased randomness source binding`

## Violated Invariant

- Invariant: EVM PREVRANDAO-style randomness should not give block proposers materially more grinding influence than the documented consensus randomness model.

## Trust Boundary

- Boundary: block proposer-controlled header fields->EVM randomness opcode consumers

## Attack Surface

- Entrypoint type: EVM block context construction
- Sensitive sink: PREVRANDAO value exposed to contracts

## Impact Pattern

- Primary impact: proposer-biased randomness
- Secondary impact: contract fairness degradation

## Short Reusable Lesson

- PREVRANDAO was derived from Time.UnixNano appended to LastCommitHash, giving proposers timestamp grinding leverage over the pseudo-random value.
