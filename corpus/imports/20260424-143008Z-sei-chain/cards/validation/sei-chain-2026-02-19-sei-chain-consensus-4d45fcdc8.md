# Validation Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-consensus-4d45fcdc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-validation`

## What Confirmed The Issue

- Evidence 1: PushQC verifies the QC only when needQC is true, and the patch makes QC insertion and ctrl.Updated() use that same guard.
- Evidence 2: The patch changes block matching to use stored, already verified QC headers instead of headers from the incoming QC.

## What Could Have Invalidated It

- Compensating control 1: All incoming QCs are verified before this function regardless of needQC.
- Compensating control 2: Later state mutation reads only canonical stored QC data.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: All incoming QCs are verified before this function regardless of needQC.
- Caution 2: Later state mutation reads only canonical stored QC data.
