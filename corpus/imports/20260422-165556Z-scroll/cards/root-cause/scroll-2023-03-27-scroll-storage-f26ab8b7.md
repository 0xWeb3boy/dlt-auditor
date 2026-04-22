# Root-Cause Card

## Metadata

- ID: `scroll-2023-03-27-scroll-storage-f26ab8b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-file-permissions`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `file-permission-hardening`

## Violated Invariant

- Invariant: Generated bridge configuration files that may hold privileged local connection material should be written with owner-only filesystem permissions.

## Trust Boundary

- Boundary: `operator-or-ci-runner->local-filesystem`

## Attack Surface

- Entrypoint type: `local-config-materialization`
- Sensitive sink: `persisted bridge configuration readable by other local principals`

## Impact Pattern

- Primary impact: `privileged-disclosure`
- Secondary impact: `none`

## Short Reusable Lesson

- Generated bridge configuration files that may hold privileged local connection material should be written with owner-only filesystem permissions. The evidence supports a narrow permission tightening in mock/CI helper code, not a demonstrated vulnerability fix. The commit is titled `fix ci`, most touched files are tests or mock helpers, and the other shown hunks are receiver renames with no evidenced security effect. The robust fix is to tighten generated-file permissions at creation time so local config artifacts default to owner-only access instead of inheriting permissive filesystem modes.
