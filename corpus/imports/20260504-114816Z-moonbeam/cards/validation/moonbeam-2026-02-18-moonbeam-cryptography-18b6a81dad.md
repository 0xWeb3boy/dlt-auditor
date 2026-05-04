# Validation Card

## Metadata

- ID: `moonbeam-2026-02-18-moonbeam-cryptography-18b6a81dad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `permit-deadline-validation`

## What Confirmed The Issue

- Permit timestamp comparison changed from timestamp/1000 to deadline*1000 >= timestamp.
- Tests cover deadline validity around the millisecond/second boundary.

## What Could Have Invalidated It

- Protocol specification intentionally permits subsecond grace after deadline
- Another check rejects the expired permit before allowance mutation

## Severity Guidance

- Expected impact band: authorization_deadline_bypass
- Expected severity band: high

## False-Positive Cautions

- If both timestamp and deadline are already same units, unit normalization is not a bug
- A grace period explicitly specified by protocol may be intentional
