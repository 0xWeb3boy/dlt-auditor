# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-underflow-branch-32706`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-underflow`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if all construction paths canonicalize values so the vulnerable branch is unreachable.
- A panic is lower severity if no user funds or queues depend on the call.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Valid signed subtraction can panic or miscompute, potentially blocking contract flows or corrupting balances.

## False-Positive Cautions

- No issue if all construction paths canonicalize values so the vulnerable branch is unreachable.
- A panic is lower severity if no user funds or queues depend on the call.
