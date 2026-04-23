# Root-Cause Card

## Metadata

- ID: `nitro-2025-07-16-nitro-storage-6821f734d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `reconstructed-canonical-validation-state`

## Violated Invariant

- Invariant: Validation should rebuild cached accumulators from persisted canonical partials before use and gate pruning or head updates on explicit safety conditions.

## Trust Boundary

- Boundary: `cached validation state->MEL validation and pruning logic`

## Attack Surface

- Entrypoint type: `validation-or-pruning`
- Sensitive sink: `accepting delayed-message state or pruning supporting data`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Validation should rebuild cached accumulators from persisted canonical partials before use and gate pruning or head updates on explicit safety conditions. The evidence supports a consensus-sensitive correctness hardening change in MEL state handling, not a confirmed vulnerability fix. The patch makes delayed-message validation tolerate a missing cached accumulator by rebuilding it from persisted partials, adds a batched head-state save path, and narrows backlog trimming to finalized-and-read entries. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
