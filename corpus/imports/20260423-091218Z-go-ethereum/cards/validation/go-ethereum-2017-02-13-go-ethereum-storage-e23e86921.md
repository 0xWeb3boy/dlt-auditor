# Validation Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`

## What Confirmed The Issue

- Evidence 1: The network store-request path now hashes `req.SData` and rejects the request if it does not match `req.Key`.
- Evidence 2: The database retrieval path also hardens mismatch cleanup by removing corrupt entries through the indexed deletion helper.

## What Could Have Invalidated It

- Compensating control 1: The system already guaranteed content-integrity verification in a lower layer before any store request reached this path.
- Compensating control 2: The key was not actually intended to be content-derived, making the digest comparison non-security-relevant.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Bound the claim to chunk-integrity hardening; do not infer consensus or RCE impact.
- Caution 2: Cleanup and panic behavior are supporting evidence, but the core security signal is the new payload-to-key comparison.
