# Validation Card

## Metadata

- ID: `avalanchego-2026-03-25-avalanchego-staking-fc749bb8c1`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow-hardening`

## What Confirmed The Issue

- Evidence: Unchecked uint64 addition of validator weight plus accrued rewards was replaced with safemath.Add.
- Evidence: The changed calculation is in loadCurrentValidators, a validator state reconstruction path.
- Evidence: The commit subject explicitly identifies an overflow in auto-renewed validator weight.

## What Could Have Invalidated It

- Compensating control: No evidence that an attacker can cause the overflowing metadata through valid protocol actions.
- Compensating control: No demonstrated consensus split, node crash, asset loss, or privilege bypass.
- Compensating control: No evidence that the secondary GetTx error handling change fixes a security issue.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: medium_or_low
- Severity rationale: Unchecked arithmetic in validator accounting is consensus-sensitive, but attacker-controlled overflow and concrete impact are not established.

## False-Positive Cautions

- Caution: Treat as security hardening, not a confirmed exploitable vulnerability.
- Caution: Do not claim fund theft, authorization bypass, or remote denial of service from the supplied evidence.
- Caution: The supported root cause is unchecked arithmetic in validator weight reconstruction.
