# Validation Card

## Metadata

- ID: `rippled-2023-08-18-rippled-consensus-e8a7b2a1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-management`

## What Confirmed The Issue

- Evidence 1: Consensus documentation now explicitly warns against advancing to a ledger that has not become validated.
- Evidence 2: Patch notes describe retrying with a new consensus transaction set if the accepted ledger does not become validated.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated malicious peer or validator exploit path.
- Compensating control 2: No proof of fund loss, double spend, ledger corruption, or authorization bypass.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: consensus-safety, network-liveness
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No demonstrated malicious peer or validator exploit path.
- Caution 2: No proof of fund loss, double spend, ledger corruption, or authorization bypass.
