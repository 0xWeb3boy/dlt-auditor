# Validation Card

## Metadata

- ID: `rippled-2024-11-05-rippled-core-logic-ec61f5e9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-reserve-check`

## What Confirmed The Issue

- Evidence 1: AMMWithdraw now defines a sufficientReserve helper with an explicit comment about checking reserve when a trustline has to be created.
- Evidence 2: The amount2WithdrawActual path now calls sufficientReserve before accountSend and exits early on error.

## What Could Have Invalidated It

- Compensating control 1: No full helper body is provided showing the exact reserve calculation and error behavior.
- Compensating control 2: No accountSend implementation evidence proves the prior path always missed reserve enforcement.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: reserve-enforcement, protocol-invariant
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No full helper body is provided showing the exact reserve calculation and error behavior.
- Caution 2: No accountSend implementation evidence proves the prior path always missed reserve enforcement.
