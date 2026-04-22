# Validation Card

## Metadata

- ID: `base-2026-04-16-base-consensus-6381f6a83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-fallback-liveness`

## What Confirmed The Issue

- Evidence 1: The commit message says a failed TEE nullification transaction caused infinite retries and required manual restart to trigger ZK fallback.
- Evidence 2: The patch stores a pre-built ZK fallback request and intent alongside pending TEE proofs.

## What Could Have Invalidated It

- Compensating control 1: Treat this as hardening of challenger/dispute liveness, not as proof of an exploitable protocol vulnerability.
- Compensating control 2: Do not claim consensus failure, fund loss, or attacker-triggered bypass from the provided patch alone.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Treat this as hardening of challenger/dispute liveness, not as proof of an exploitable protocol vulnerability.
- Caution 2: Do not claim consensus failure, fund loss, or attacker-triggered bypass from the provided patch alone.
