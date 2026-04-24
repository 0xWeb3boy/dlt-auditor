# Validation Card

## Metadata

- ID: `rippled-2025-11-14-rippled-core-logic-362ecbd1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting`

## What Confirmed The Issue

- Evidence 1: VaultCreate changes OwnerCount adjustment from +1 to +2 before enforcing account reserve.
- Evidence 2: VaultDelete changes OwnerCount adjustment from -1 to -2, matching destruction of both Vault and PseudoAccount.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated exploit path showing network-level denial of service or ledger bloat at scale.
- Compensating control 2: No evidence of unauthorized vault access, asset theft, withdrawal, or takeover.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: reserve-undercharging, ledger-state-accounting
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No demonstrated exploit path showing network-level denial of service or ledger bloat at scale.
- Caution 2: No evidence of unauthorized vault access, asset theft, withdrawal, or takeover.
