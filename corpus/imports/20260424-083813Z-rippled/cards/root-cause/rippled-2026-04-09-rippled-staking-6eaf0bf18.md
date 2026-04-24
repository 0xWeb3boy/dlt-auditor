# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-09-rippled-staking-6eaf0bf18`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-lifecycle-cleanup`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: stale-authorization-state, incomplete-account-cleanup
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch adds bidirectional owner-directory tracking for Delegate ledger entries. Creation now inserts the Delegate object into the authorized account's owner directory and stores the page in optional sfDestinationNode; deletion now removes the object from that authorized account directory when sfDestinationNode is present.
