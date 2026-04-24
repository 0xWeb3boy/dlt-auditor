# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-6f86ef9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: exact checkpoint continuity validation and fail-closed buffer handling.

## Violated Invariant

- Invariant: checkpoint admission and post-handle code must reject skipped block ranges and must not continue with buffer-dependent logic after buffer read failure.

## Trust Boundary

- Boundary: checkpoint message and side-transaction result crossing into persistent checkpoint state.

## Attack Surface

- Entrypoint type: checkpoint transaction handler plus side-transaction post-handler.
- Sensitive sink: checkpoint keeper state, checkpoint buffer, and downstream checkpoint submission flow.

## Impact Pattern

- Primary impact: checkpoint-integrity hardening.
- Secondary impact: state-integrity hardening under storage read failures.

## Short Reusable Lesson

- Duplicated admission paths for the same protocol object must enforce the same range invariant. A direct handler and post-consensus handler should both use exact continuity checks and should fail closed on real buffer read errors.
