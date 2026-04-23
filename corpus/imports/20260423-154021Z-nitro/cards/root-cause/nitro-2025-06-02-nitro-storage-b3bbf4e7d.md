# Root-Cause Card

## Metadata

- ID: `nitro-2025-06-02-nitro-storage-b3bbf4e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-delayed-message-validation`

## Violated Invariant

- Invariant: Delayed-message or MEL validation should reconstruct the relevant accumulator context and perform the full set of checks instead of placeholder success paths.

## Trust Boundary

- Boundary: `delayed-message extraction data->native validation path`

## Attack Surface

- Entrypoint type: `validation-or-accumulator-checking`
- Sensitive sink: `marking delayed-message data as valid or advancing validation state`

## Impact Pattern

- Primary impact: `integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- Delayed-message or MEL validation should reconstruct the relevant accumulator context and perform the full set of checks instead of placeholder success paths. The provided evidence supports that this patch implements previously missing delayed-message accumulation and accumulator checks in native-mode MEL. It does not, by itself, establish that the prior behavior was a proven exploitable vulnerability rather than an incomplete or unfinished validation path. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
