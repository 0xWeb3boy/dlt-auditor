# Root-Cause Card

## Metadata

- ID: `nitro-2022-04-10-nitro-transaction-processing-3a9ee3753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `artifact-identity-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `artifact-identity-binding`

## Violated Invariant

- Invariant: Artifact aliases or convenience selectors should resolve to a canonical identity, and the loaded artifact should prove that same identity before initialization continues.

## Trust Boundary

- Boundary: `operator-selected artifact alias->machine loader and initialization`

## Attack Surface

- Entrypoint type: `machine-loading-or-initialization`
- Sensitive sink: `accepting a loaded artifact for staker or validator use`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Artifact aliases or convenience selectors should resolve to a canonical identity, and the loaded artifact should prove that same identity before initialization continues. The patch adds explicit module-root canonicalization and a root-match check when loading validator machines, and it wires staker initialization through loader-based latest-root update logic. That supports a correctness or integrity-hardening reading, but the provided evidence does not establish a demonstrated vulnerability. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
