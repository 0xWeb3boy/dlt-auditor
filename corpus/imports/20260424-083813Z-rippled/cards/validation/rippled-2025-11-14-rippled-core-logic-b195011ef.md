# Validation Card

## Metadata

- ID: `rippled-2025-11-14-rippled-core-logic-b195011ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting`

## What Confirmed The Issue

- Evidence 1: VaultCreate changes OwnerCount adjustment from 1 to 2 before checking accountReserve, matching creation of both Vault and PseudoAccount.
- Evidence 2: VaultDelete changes OwnerCount adjustment from -1 to -2, making deletion accounting symmetric with creation.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows an authorization bypass or privilege misuse.
- Compensating control 2: No evidence demonstrates theft, unauthorized withdrawal, or direct asset loss.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: under-reserved-ledger-state
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No evidence shows an authorization bypass or privilege misuse.
- Caution 2: No evidence demonstrates theft, unauthorized withdrawal, or direct asset loss.
