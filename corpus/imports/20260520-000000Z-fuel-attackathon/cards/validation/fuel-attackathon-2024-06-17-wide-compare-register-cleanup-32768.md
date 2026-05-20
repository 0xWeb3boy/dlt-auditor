# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-wide-compare-register-cleanup-32768`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reserved-register-stale-state`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the spec intentionally allows the register to persist.
- No issue if the register value is not observable or branchable after the opcode.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Stale VM status registers can cause valid bytecode to take wrong branches; impact depends on contract logic.

## False-Positive Cautions

- No issue if the spec intentionally allows the register to persist.
- No issue if the register value is not observable or branchable after the opcode.
