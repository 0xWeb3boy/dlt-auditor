# Root-Cause Card

## Metadata

- ID: `nitro-2026-01-14-nitro-storage-9b7a73c97`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `validation-progress-gating`

## Violated Invariant

- Invariant: New validator work should be gated on the relevant validated-message progress so block validation does not outrun extraction validation.

## Trust Boundary

- Boundary: `validated-message progress->block-validator work scheduling`

## Attack Surface

- Entrypoint type: `work-scheduling-or-validation-gating`
- Sensitive sink: `creating new block-validation work on insufficiently validated state`

## Impact Pattern

- Primary impact: `validation-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- New validator work should be gated on the relevant validated-message progress so block validation does not outrun extraction validation. The patch adds an explicit MEL validated-message-count gate before block validation creates new work, adjusts MEL validator progress tracking, and changes MEL state hash construction. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
