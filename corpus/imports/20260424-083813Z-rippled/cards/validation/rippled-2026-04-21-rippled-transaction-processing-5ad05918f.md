# Validation Card

## Metadata

- ID: `rippled-2026-04-21-rippled-transaction-processing-5ad05918f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-structural-validation`

## What Confirmed The Issue

- Evidence 1: Post-fix logic rejects hybrid offers unless sfAdditionalBooks is present with exactly one entry.
- Evidence 2: The old predicate rejected missing sfAdditionalBooks and size greater than one, but not a present empty array.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows how an empty sfAdditionalBooks hybrid offer could be created or accepted into the ledger.
- Compensating control 2: No evidence demonstrates theft, fund loss, unauthorized trading, or economic distortion.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: protocol-invariant-enforcement
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence shows how an empty sfAdditionalBooks hybrid offer could be created or accepted into the ledger.
- Caution 2: No evidence demonstrates theft, fund loss, unauthorized trading, or economic distortion.
