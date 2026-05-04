# Root-Cause Card

## Metadata

- ID: `moonbeam-2026-02-18-moonbeam-cryptography-18b6a81dad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `permit-deadline-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `deadline-unit-consistency`

## Violated Invariant

- Invariant: Signed authorization deadlines must be compared in consistent units and fail closed on overflow before approving state changes.

## Trust Boundary

- Boundary: Externally signed permit data crosses into runtime token allowance mutation.

## Attack Surface

- Entrypoint type: erc20-permit-precompile
- Sensitive sink: permit allowance authorization

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: signature-expiration-bypass, allowance-misuse

## Short Reusable Lesson

- The permit guard divided the current millisecond timestamp by 1000, creating a floor-rounding window. The fix multiplies the deadline to milliseconds with checked_mul and compares directly. Normalize deadline and current time to the same unit, use checked arithmetic for conversion, and reject expired or overflowing permits.
