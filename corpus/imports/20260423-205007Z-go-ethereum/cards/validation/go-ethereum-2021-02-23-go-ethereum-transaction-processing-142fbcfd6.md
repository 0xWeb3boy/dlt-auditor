# Validation Card

## Metadata

- ID: `go-ethereum-2021-02-23-go-ethereum-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-enforcement`

## What Confirmed The Issue

- Evidence 1: SubmitTransaction now rejects transactions where tx.Protected() is false unless UnprotectedAllowed() is enabled.
- Evidence 2: The returned error explicitly says only replay-protected EIP-155 transactions are allowed over RPC.

## What Could Have Invalidated It

- Compensating control 1: Classify as default-policy security hardening, not a proven vulnerability fix.
- Compensating control 2: Do not claim state corruption is demonstrated by the patch.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as default-policy security hardening, not a proven vulnerability fix.
- Caution 2: Do not claim state corruption is demonstrated by the patch.
