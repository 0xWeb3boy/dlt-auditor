# Validation Card

## Metadata

- ID: `sei-chain-2022-02-02-sei-chain-core-logic-a613471d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism`

## What Confirmed The Issue

- Evidence 1: Transfer OnRecvPacket changed from channeltypes.NewErrorAcknowledgement(err.Error()) to types.NewErrorAcknowledgement(err).
- Evidence 2: Core acknowledgement comment states acknowledgement error strings are written into state and can risk app hash divergence.

## What Could Have Invalidated It

- Compensating control 1: The error text is never committed or included in consensus results.
- Compensating control 2: All possible error strings are protocol constants identical across versions.

## Severity Guidance

- Expected impact band: consensus-integrity-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The error text is never committed or included in consensus results.
- Caution 2: All possible error strings are protocol constants identical across versions.
