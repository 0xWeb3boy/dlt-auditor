# Validation Card

## Metadata

- ID: `go-ethereum-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-configuration-hardening`

## What Confirmed The Issue

- Evidence 1: checkCompatible now rejects incompatible MetropolisBlock settings using isForkIncompatible.
- Evidence 2: The new error path labels the mismatch as "Metropolis fork block", aligning it with existing fork compatibility checks.

## What Could Have Invalidated It

- Compensating control 1: Classify as consensus configuration hardening, not a confirmed security fix.
- Compensating control 2: Do not claim transaction-processing, signature, replay, or VM impact from this evidence.

## Severity Guidance

- Expected impact band: high
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify as consensus configuration hardening, not a confirmed security fix.
- Caution 2: Do not claim transaction-processing, signature, replay, or VM impact from this evidence.
