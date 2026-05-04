# Validation Card

## Metadata

- ID: `stellar-core-2024-07-17-stellar-core-core-logic-ebef6c368`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hash-collision-dos-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- BinaryFuseFilter switched population and lookup hashing to SipHash24.
- Population retry behavior changed from unbounded to a maximum of 10 attempts.

## What Could Have Invalidated It

- If inputs are generated only by trusted local code and cannot be influenced, severity drops.
- If construction failure is already cheap and nonfatal, retry cap matters less.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Keyed hashing and retry caps reduce algorithmic DoS risk, but the finding does not prove a concrete production exploit path.

## False-Positive Cautions

- Do not flag every MurmurHash use; focus on chosen-input, collision-sensitive, high-cost structures.
- Check for existing seeding and input caps before rating DoS risk.
