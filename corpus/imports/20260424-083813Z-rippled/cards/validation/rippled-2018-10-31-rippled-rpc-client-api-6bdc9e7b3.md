# Validation Card

## Metadata

- ID: `rippled-2018-10-31-rippled-rpc-client-api-6bdc9e7b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wrong-revocation-cache`

## What Confirmed The Issue

- Evidence 1: ValidatorList::load parses a configured validator-list publisher key into id.
- Evidence 2: Before the patch, revocation was checked with validatorManifests_.revoked(id).

## What Could Have Invalidated It

- Compensating control 1: No test contents are provided to show the exact regression scenario.
- Compensating control 2: No evidence shows live exploitation or production impact.

## Severity Guidance

- Expected impact band: security-impact: revocation-bypass, trust-validation-bypass
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No test contents are provided to show the exact regression scenario.
- Caution 2: No evidence shows live exploitation or production impact.
