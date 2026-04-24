# Validation Card

## Metadata

- ID: `sei-chain-2025-09-30-sei-chain-transaction-processing-caebdeaa5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-panic-hardening`

## What Confirmed The Issue

- Evidence 1: ProcessBlock now recovers non-upgrade panics and returns an error instead of allowing the panic to escape.
- Evidence 2: ProcessProposalHandler optimistic processing now checks ProcessBlock errors and marks optimistic processing aborted.

## What Could Have Invalidated It

- Compensating control 1: Panics are impossible for attacker-controlled input or are recovered at a higher consensus boundary.
- Compensating control 2: The failed path is simulation-only and cannot affect proposal acceptance.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Panics are impossible for attacker-controlled input or are recovered at a higher consensus boundary.
- Caution 2: The failed path is simulation-only and cannot affect proposal acceptance.
