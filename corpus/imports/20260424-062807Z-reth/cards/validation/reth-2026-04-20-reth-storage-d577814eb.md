# Validation Card

## Metadata

- ID: `reth-2026-04-20-reth-storage-d577814eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation`

## What Confirmed The Issue

- The changed function validate_block_access_list_presence is an Engine API boundary validator and now gives EngineApiMessageVersion::V5 its own branch instead of grouping it with V1-V4.
- The new V5 payload-specific logic ties acceptance requirements to is_amsterdam_active, indicating stricter fork-aware validation rather than a broad version cutoff.

## What Could Have Invalidated It

- No test, trace, advisory, or issue text shows malformed payloads were previously accepted in practice
- No evidence shows chain-state corruption, consensus split, remote exploitation, or attacker-controlled impact

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No test, trace, advisory, or issue text shows malformed payloads were previously accepted in practice
- No evidence shows chain-state corruption, consensus split, remote exploitation, or attacker-controlled impact
