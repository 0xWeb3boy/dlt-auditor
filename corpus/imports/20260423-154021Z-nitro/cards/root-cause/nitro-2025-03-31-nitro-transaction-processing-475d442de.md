# Root-Cause Card

## Metadata

- ID: `nitro-2025-03-31-nitro-transaction-processing-475d442de`
- Bug family: `authz_and_role_gates`
- Bug class: `stale-authorization-state`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fresh-authorization-binding`

## Violated Invariant

- Invariant: Privileged submissions should be authorized against fresh round or controller state from the authoritative tracker before deeper processing or sequencing.

## Trust Boundary

- Boundary: `network submission->express-lane authorization and sequencing`

## Attack Surface

- Entrypoint type: `transaction-or-message-admission`
- Sensitive sink: `accepting or sequencing a privileged transaction`

## Impact Pattern

- Primary impact: `unauthorized-transaction-acceptance-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- Privileged submissions should be authorized against fresh round or controller state from the authoritative tracker before deeper processing or sequencing. The patch is clearly hardening the express-lane admission path against stale or improperly validated submissions, but the provided evidence does not firmly establish a concrete vulnerability beyond correctness and fail-closed behavior. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
