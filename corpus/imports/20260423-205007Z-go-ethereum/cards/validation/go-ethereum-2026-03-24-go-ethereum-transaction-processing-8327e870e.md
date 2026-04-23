# Validation Card

## Metadata

- ID: `go-ethereum-2026-03-24-go-ethereum-transaction-processing-8327e870e`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-ordering`

## What Confirmed The Issue

- Evidence 1: Patch comments explicitly state the new ordering prevents reservoir inflation when regular gas charging OOGs.
- Evidence 2: CALL-family logic now charges intrinsic regular gas before computing or charging state gas and describes this as the OOG guard before stateful operations.

## What Could Have Invalidated It

- Compensating control 1: Classify as hardening of gas-accounting invariants, not proven state corruption.
- Compensating control 2: Do not claim confirmed vulnerability or exploitability from the supplied evidence.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify as hardening of gas-accounting invariants, not proven state corruption.
- Caution 2: Do not claim confirmed vulnerability or exploitability from the supplied evidence.
