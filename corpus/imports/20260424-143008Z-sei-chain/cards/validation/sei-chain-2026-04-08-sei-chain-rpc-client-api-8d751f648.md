# Validation Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-rpc-client-api-8d751f648`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protobuf-input-validation`

## What Confirmed The Issue

- Evidence 1: TimeoutQCConv.Decode now rejects decoded TimeoutQC messages with zero votes using a "votes: missing" error.
- Evidence 2: A regression test asserts that decoding an empty pb.TimeoutQC must fail.

## What Could Have Invalidated It

- Compensating control 1: The malformed object can only be constructed in tests and never from network/storage input.
- Compensating control 2: A later Verify call always rejects it before use.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The malformed object can only be constructed in tests and never from network/storage input.
- Caution 2: A later Verify call always rejects it before use.
