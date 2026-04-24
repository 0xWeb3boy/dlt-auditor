# Validation Card

## Metadata

- ID: `rippled-2026-04-10-rippled-core-logic-24241a6f9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `asset-restriction-enforcement`

## What Confirmed The Issue

- Evidence 1: CheckCreate now propagates checkGlobalFrozen TER results instead of using a simpler boolean frozen check.
- Evidence 2: CheckCreate MPT handling adds canTransfer enforcement after per-account frozen checks.

## What Could Have Invalidated It

- Compensating control 1: No advisory, issue text, or commit body explicitly states a security vulnerability.
- Compensating control 2: No proof that the prior behavior enabled theft, unauthorized minting or burning, or unauthorized asset movement.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: policy-bypass
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No advisory, issue text, or commit body explicitly states a security vulnerability.
- Caution 2: No proof that the prior behavior enabled theft, unauthorized minting or burning, or unauthorized asset movement.
