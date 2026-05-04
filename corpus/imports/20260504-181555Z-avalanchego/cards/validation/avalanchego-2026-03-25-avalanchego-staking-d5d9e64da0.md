# Validation Card

## Metadata

- ID: `avalanchego-2026-03-25-avalanchego-staking-d5d9e64da0`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `unchecked-validator-weight-overflow`

## What Confirmed The Issue

- Evidence: Unchecked addition of validator weight plus accrued rewards was replaced with checked safemath.Add calls.
- Evidence: Overflow now returns an explicit error instead of silently wrapping uint64 weight.
- Evidence: The changed path loads current validators and reconstructs auto-renewed validator staking weight from persisted metadata.

## What Could Have Invalidated It

- Compensating control: No proof that an external actor can force overflowing accrued reward metadata.
- Compensating control: No demonstrated consensus split, funds loss, node crash, or denial of service scenario.
- Compensating control: No invariant or test output showing the pre-patch wrapped weight causing a concrete security failure.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: medium_or_low
- Severity rationale: Unchecked arithmetic in validator accounting is consensus-sensitive, but attacker-controlled overflow and concrete impact are not established.

## False-Positive Cautions

- Caution: Classify as security-hardening, not a proven exploitable vulnerability.
- Caution: Do not claim access-control or privilege-check impact from the provided test/helper changes.
- Caution: Do not claim funds loss or consensus failure beyond potential validator-weight integrity risk.
