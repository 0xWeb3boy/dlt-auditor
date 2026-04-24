# Root-Cause Card

## Metadata

- ID: `rippled-2013-01-18-rippled-access-control-bda80d414`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
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

- Primary impact: privilege-misuse
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch is security-relevant and likely hardens RPC admin access, but the supplied evidence does not fully prove an exploitable authorization bypass.
