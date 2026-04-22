# Validation Card

## Metadata

- ID: `base-2024-06-27-base-cryptography-bfe0dd435`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-hardening`

## What Confirmed The Issue

- Evidence 1: `InMemoryOracle::verify` is an integrity-checking path that validates cached values against derived keys and per-type rules.
- Evidence 2: The patch adds typed `PreimageKey` canonicalization before dispatch, tightening how verification interprets cache keys.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the patch hardens verification of precompile-backed oracle entries by recomputing and checking expected outputs.
- Compensating control 2: Supported claim: some surrounding edits are type/canonicalization changes needed for the revised verification flow.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the patch hardens verification of precompile-backed oracle entries by recomputing and checking expected outputs.
- Caution 2: Supported claim: some surrounding edits are type/canonicalization changes needed for the revised verification flow.
