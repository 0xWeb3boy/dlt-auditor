# Root-Cause Card

## Metadata

- ID: `nitro-2022-03-17-nitro-storage-368fbe57c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-artifact-integrity`

## Violated Invariant

- Invariant: Validator startup should reject inconsistent data-availability settings and runtime artifacts whose measured module root does not match the configured root.

## Trust Boundary

- Boundary: `operator configuration and loaded artifact->validator startup`

## Attack Surface

- Entrypoint type: `node-startup-or-configuration`
- Sensitive sink: `starting a validator with a selected runtime artifact and DA mode`

## Impact Pattern

- Primary impact: `integrity-protection`
- Secondary impact: `fail-safe-startup`

## Short Reusable Lesson

- Validator startup should reject inconsistent data-availability settings and runtime artifacts whose measured module root does not match the configured root. The visible patch adds fail-fast validation in the validator startup path, including configuration sanity checks and a runtime WASM module-root comparison. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
