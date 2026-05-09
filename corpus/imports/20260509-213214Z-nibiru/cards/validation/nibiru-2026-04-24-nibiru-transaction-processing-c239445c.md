# Validation Card

## Metadata

- ID: `nibiru-2026-04-24-nibiru-transaction-processing-c239445c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-vm-callback-guard`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: FunToken sendToEvm and Wasm execute native state transitions.
- Evidence 2: The validated finding ties the change to this invariant: Mutable native precompile methods must reject calls made while execution is inside a VM-originated contract callback or module-caller context.

## What Could Have Invalidated It

- Compensating control 1: Read-only precompile methods may be safe in callback context
- Compensating control 2: Do not claim fund theft without a demonstrated privileged sink and preserved caller

## Severity Guidance

- Expected impact band: `state_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Privileged callback context reaching mutable native sinks can be severe, but this finding is kept as likely hardening because the full exploit path was not proven in the report.
