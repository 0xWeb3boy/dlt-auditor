# Validation Card

## Metadata

- ID: `base-2026-04-20-base-transaction-processing-88b36d5a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-guard`

## What Confirmed The Issue

- Evidence 1: A new shared `build_cfg_env` helper sets `cfg_env.tx_gas_limit_cap = Some(MAX_TX_GAS_LIMIT_OSAKA)` when Base V1 is active.
- Evidence 2: Two EVM environment construction paths were changed from inline `CfgEnv` creation to the shared helper, reducing path-dependent omission of the cap.

## What Could Have Invalidated It

- Compensating control 1: The evidence supports a missing fork-specific gas-limit guard in some EVM environment builders.
- Compensating control 2: The evidence supports classifying this as security hardening because it tightens a runtime policy in a sensitive execution path.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The evidence supports a missing fork-specific gas-limit guard in some EVM environment builders.
- Caution 2: The evidence supports classifying this as security hardening because it tightens a runtime policy in a sensitive execution path.
