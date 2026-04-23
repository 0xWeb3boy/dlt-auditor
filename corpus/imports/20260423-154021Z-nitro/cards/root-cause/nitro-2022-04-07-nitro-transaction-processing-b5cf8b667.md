# Root-Cause Card

## Metadata

- ID: `nitro-2022-04-07-nitro-transaction-processing-b5cf8b667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `module-root-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `module-root-binding`

## Violated Invariant

- Invariant: Challenge or validator machine loading should select the artifact by the requested module root and confirm the loaded machine reports that same root before use.

## Trust Boundary

- Boundary: `challenge metadata or config->machine loader`

## Attack Surface

- Entrypoint type: `machine-loading-or-challenge-setup`
- Sensitive sink: `loading a machine artifact for validator or challenge execution`

## Impact Pattern

- Primary impact: `validator-misexecution`
- Secondary impact: `none`

## Short Reusable Lesson

- Challenge or validator machine loading should select the artifact by the requested module root and confirm the loaded machine reports that same root before use. The patch changes challenge-related machine loading so the validator can select a machine by module root instead of implicitly using the latest machine directory, and it adds an explicit module-root equality check before using the loaded machine. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
