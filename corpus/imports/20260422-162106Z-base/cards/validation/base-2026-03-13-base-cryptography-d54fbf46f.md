# Validation Card

## Metadata

- ID: `base-2026-03-13-base-cryptography-d54fbf46f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-integrity`

## What Confirmed The Issue

- Evidence 1: The commit subject/body explicitly says enclave configuration was removed and enclave parameters were hardcoded.
- Evidence 2: `PerChainConfig::from_rollup_config` derives per-chain values from `RollupConfig` and returns `None` when required system config is absent.

## What Could Have Invalidated It

- Compensating control 1: Supported: the patch hardens enclave configuration selection and supported-chain enforcement.
- Compensating control 2: Supported: the change reduces ambiguity by pinning config hashes to known chains and rejecting unknown ones.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported: the patch hardens enclave configuration selection and supported-chain enforcement.
- Caution 2: Supported: the change reduces ambiguity by pinning config hashes to known chains and rejecting unknown ones.
