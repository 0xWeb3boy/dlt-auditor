# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m01-prevrandao-proposer-bias`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `proposer-biased-randomness-source`

## Code Shape Summary

- PREVRANDAO was derived from Time.UnixNano appended to LastCommitHash, giving proposers timestamp grinding leverage over the pseudo-random value.

## Search Motifs

- PREVRANDAO pseudoRandomBytes Time.UnixNano
- LastCommitHash keccak randomness
- EIP-4399 biasability
- randao support EVM

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Use a consensus-provided randomness source with documented bias bounds, keep PREVRANDAO zero, or clearly document non-Ethereum randomness semantics.

## False Match Warnings

- No issue if PREVRANDAO remains documented as zero or non-random.
- No issue if source randomness comes from an unbiased consensus beacon.
- No issue if contracts cannot access or rely on the value.
