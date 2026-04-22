# Validation Card

## Metadata

- ID: `base-2026-03-29-base-transaction-processing-6c11aa61d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: EOA-mode sender resolution now requires an explicit recovered sender instead of implicitly using the transaction helper.
- Evidence 2: Config-change sequence validation now reads state with the threaded validated sender rather than `tx.effective_sender()`.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the commit hardens validation and resource limits in a security-sensitive AA transaction path.
- Compensating control 2: Not supported: a confirmed exploitable auth bypass, account takeover, or state-corruption bug in pre-patch code.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Supported claim: the commit hardens validation and resource limits in a security-sensitive AA transaction path.
- Caution 2: Not supported: a confirmed exploitable auth bypass, account takeover, or state-corruption bug in pre-patch code.
