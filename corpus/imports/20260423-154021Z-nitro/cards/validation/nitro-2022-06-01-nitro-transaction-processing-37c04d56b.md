# Validation Card

## Metadata

- ID: `nitro-2022-06-01-nitro-transaction-processing-37c04d56b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `caller-controlled-withdrawal-destination`

## What Confirmed The Issue

- Evidence 1: The grounded change is that the validator client no longer accepts or passes a configurable `withdrawDestination` when withdrawing staker funds.
- Evidence 2: Remove a caller-controlled parameter from a privileged path and centralize selection or validation behind a narrower interface.

## What Could Have Invalidated It

- Compensating control 1: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
- Compensating control 2: If only trusted operators can invoke the path and the policy is documented, the issue may be operational hardening rather than a security bug.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
- Caution 2: Do not claim theft or validator compromise without evidence that the unsafe choice reaches the final sink.
