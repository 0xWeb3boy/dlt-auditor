# Validation Card

## Metadata

- ID: `firedancer-2024-05-28-firedancer-cryptography-32b9530a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `retry-token-forgery`

## What Confirmed The Issue

- Evidence 1: Commit subject states Retry tokens now include a per-instance secret so clients cannot spoof the token.
- Evidence 2: QUIC initialization now generates and stores state->retry_secret for future Retry token generation.

## What Could Have Invalidated It

- Compensating control 1: No full exploit trace or proof-of-concept is provided.
- Compensating control 2: No evidence shows which deployments or configurations enabled Retry tokens.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No full exploit trace or proof-of-concept is provided.
- Caution 2: No evidence shows which deployments or configurations enabled Retry tokens.
