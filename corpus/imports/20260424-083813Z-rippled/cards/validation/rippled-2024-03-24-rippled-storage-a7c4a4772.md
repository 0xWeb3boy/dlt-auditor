# Validation Card

## Metadata

- ID: `rippled-2024-03-24-rippled-storage-a7c4a4772`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `amm-offer-overflow-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject and body describe improper handling of large synthetic AMM offers in the payment engine.
- Evidence 2: Overflow handling in AMMLiquidity::getOffer changes from returning maxOffer after overflow to returning std::nullopt when fixAMMOverflowOffer is enabled.

## What Could Have Invalidated It

- Compensating control 1: No exploit reproduction or attack scenario is provided.
- Compensating control 2: No implementation of checkInvariant is shown in the supplied evidence.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-integrity, economic-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit reproduction or attack scenario is provided.
- Caution 2: No implementation of checkInvariant is shown in the supplied evidence.
