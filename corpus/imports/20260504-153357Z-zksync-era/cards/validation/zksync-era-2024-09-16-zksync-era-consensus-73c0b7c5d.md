# Validation Card

## Metadata

- ID: `zksync-era-2024-09-16-zksync-era-consensus-73c0b7c5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-management-hardening`

## What Confirmed The Issue

- Evidence 1: The workflow builds privileged L1 deployment transactions without signing and broadcasting them immediately.
- Evidence 2: The Forge setup path supports an explicit sender address and removes automatic broadcast behavior in the shown branch.

## What Could Have Invalidated It

- Compensating control 1: Existing production deployment processes already used offline signing and never loaded private keys into online tooling.
- Compensating control 2: The affected command is test-only or cannot produce privileged L1 transactions.

## Severity Guidance

- Expected impact band: key-management-hardening
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Do not claim a prior private-key leak without evidence.
- Caution 2: Unsigned transaction generation is operational hardening, not a consensus or accounting vulnerability by itself.
