# Validation Card

## Metadata

- ID: `reth-2025-04-25-reth-transaction-processing-82d650594`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`

## What Confirmed The Issue

- Ethereum validate_header now rejects post-Paris headers with non-zero difficulty.
- Ethereum validate_header now rejects post-Paris headers with non-zero nonce.

## What Could Have Invalidated It

- No test or reproducer is shown proving previously accepted invalid headers on a reachable path
- The full removed helper body is not provided, so prior nonce and related checks are not fully visible

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No test or reproducer is shown proving previously accepted invalid headers on a reachable path
- The full removed helper body is not provided, so prior nonce and related checks are not fully visible
