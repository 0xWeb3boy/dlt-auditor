# Validation Card

## Metadata

- ID: `sei-chain-2025-10-29-sei-chain-transaction-processing-48090d81b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-nonce-bookkeeping`

## What Confirmed The Issue

- Evidence 1: Commit describes stale pending nonces remaining after mempool rejection because rollback was not invoked on all failure paths.
- Evidence 2: Commit scenario states nonce N+1 could be promoted and become block-eligible without nonce N being included first.

## What Could Have Invalidated It

- Compensating control 1: The nonce tracker is advisory only and never affects promotion or block selection.
- Compensating control 2: All post-insert rejection paths defer a guaranteed rollback.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The nonce tracker is advisory only and never affects promotion or block selection.
- Caution 2: All post-insert rejection paths defer a guaranteed rollback.
