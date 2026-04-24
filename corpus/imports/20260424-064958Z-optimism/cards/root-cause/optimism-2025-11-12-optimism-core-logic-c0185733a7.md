# Root-Cause Card

## Metadata

- ID: `optimism-2025-11-12-optimism-core-logic-c0185733a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `archive-extraction-path-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: Archive extraction should validate member names before creating output paths, rejecting unsafe names such as absolute paths or traversal-like entries.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: path-traversal-risk-reduction
- Secondary impact: filesystem-write-confinement

## Short Reusable Lesson

- Archive extraction should validate member names before creating output paths, rejecting unsafe names such as absolute paths or traversal-like entries. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement at the boundary and fail closed before state, privilege, or consensus-visible output changes.
