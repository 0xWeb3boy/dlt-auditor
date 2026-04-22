# Validation Card

## Metadata

- ID: `base-2026-02-18-base-transaction-processing-0127d7834`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: `validate_tx` now receives `sender_code` and checks the actual bytecode rather than only account metadata.
- Evidence 2: The new guard rejects any signer with present bytecode unless `bytecode.is_eip7702()` is true.

## What Could Have Invalidated It

- Compensating control 1: Supported: the commit hardens signer validation for EIP-7702-related bytecode handling in the client metering path.
- Compensating control 2: Supported: the old logic relied on an indirect proxy and the new logic enforces a stricter invariant using actual sender code.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported: the commit hardens signer validation for EIP-7702-related bytecode handling in the client metering path.
- Caution 2: Supported: the old logic relied on an indirect proxy and the new logic enforces a stricter invariant using actual sender code.
