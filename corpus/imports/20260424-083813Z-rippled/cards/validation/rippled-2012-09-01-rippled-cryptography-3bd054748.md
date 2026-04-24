# Validation Card

## Metadata

- ID: `rippled-2012-09-01-rippled-cryptography-3bd054748`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-duplicate-suppression-bypass`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly calls the issue a vulnerability.
- Evidence 2: Subject describes attacker-observable proposal replay/mutation leading to suppression of the real proposal.

## What Could Have Invalidated It

- Compensating control 1: No tests are supplied showing the malformed-proposal scenario.
- Compensating control 2: No surrounding validity-check code is supplied to prove the exact ordering of duplicate suppression versus validation.

## Severity Guidance

- Expected impact band: security-impact: consensus-message-suppression, denial-of-service
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No tests are supplied showing the malformed-proposal scenario.
- Caution 2: No surrounding validity-check code is supplied to prove the exact ordering of duplicate suppression versus validation.
