# Validation Card

## Metadata

- ID: `avalanchego-2025-01-27-avalanchego-storage-9e729ab76c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-resource-control`

## What Confirmed The Issue

- Evidence: FeeHistory now rejects rewardPercentiles arrays longer than maxQueryLimit.
- Evidence: The bounded value is caller-provided input to a fee history API path.
- Evidence: The change is explicitly resource-control behavior: cardinality limiting before further validation and processing.

## What Could Have Invalidated It

- Compensating control: No exploit, benchmark, or concrete denial-of-service threshold is provided.
- Compensating control: No advisory, CVE, test, or commit message detail confirms a vulnerability.
- Compensating control: No evidence supports consensus divergence, state corruption, cryptographic failure, or replay failure.

## Severity Guidance

- Expected impact band: medium_availability
- Expected severity band: medium_or_low
- Severity rationale: Unbounded RPC arrays can cause avoidable resource usage, but the evidence does not quantify a denial of service.

## False-Positive Cautions

- Caution: Classify only as RPC resource-control hardening, not a confirmed security fix.
- Caution: Do not retain the original state-corruption or state-integrity framing.
- Caution: Do not treat the comment-only snapshot change as security evidence.
