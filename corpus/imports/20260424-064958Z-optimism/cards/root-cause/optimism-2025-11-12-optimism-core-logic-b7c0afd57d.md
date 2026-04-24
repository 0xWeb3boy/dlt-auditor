# Root-Cause Card

## Metadata

- ID: `optimism-2025-11-12-optimism-core-logic-b7c0afd57d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `archive-path-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: When untarring deployment artifacts, archive entry names should resolve only to intended paths under the chosen output directory, and obviously unsafe names such as absolute paths should be rejected before files are written.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: out-of-directory-file-write
- Secondary impact: host-filesystem-integrity

## Short Reusable Lesson

- When untarring deployment artifacts, archive entry names should resolve only to intended paths under the chosen output directory, and obviously unsafe names such as absolute paths should be rejected before files are written. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement at the boundary and fail closed before state, privilege, or consensus-visible output changes.
