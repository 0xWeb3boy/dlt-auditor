# Validation Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-transaction-processing-63751c1d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`

## What Confirmed The Issue

- Evidence 1: ALUT resolution is in a blockchain transaction-processing path tied to bank, slot, replay, and Funk state.
- Evidence 2: Patch replaces NULL root Funk transaction use with a slot-derived fd_funk_txn_xid_t passed to fd_runtime_load_txn_address_lookup_tables.

## What Could Have Invalidated It

- Compensating control 1: No advisory, issue discussion, or commit body states a security vulnerability.
- Compensating control 2: No exploit path or attacker-controlled timing is shown.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No advisory, issue discussion, or commit body states a security vulnerability.
- Caution 2: No exploit path or attacker-controlled timing is shown.
