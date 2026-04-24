# Validation Card

## Metadata

- ID: `rippled-2026-03-21-rippled-core-logic-311719dae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-state-overwrite`

## What Confirmed The Issue

- Evidence 1: Commit body states invariant checks used assignment instead of accumulated OR, allowing later entries to overwrite earlier violations.
- Evidence 2: Affected code is in transaction invariant finalizers for NoZeroEscrow, NoXRPTrustLines, and NoDeepFreezeTrustLinesWithoutFreeze.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated transaction path showing an attacker can create the invalid states.
- Compensating control 2: No proof that the bug caused consensus divergence, fund loss, authorization bypass, or privilege misuse.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity, consensus-safety
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No demonstrated transaction path showing an attacker can create the invalid states.
- Caution 2: No proof that the bug caused consensus divergence, fund loss, authorization bypass, or privilege misuse.
