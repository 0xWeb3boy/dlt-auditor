# Root-Cause Card

## Metadata

- ID: `rippled-2025-10-31-rippled-transaction-processing-fa6991812`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: authorization-bypass, unauthorized-delegated-transaction
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The patch addresses a permission-delegation authorization flaw. The strongest supported claim is that delegated transaction permission checks were not consistently tied to the current amendment-aware delegability rules and the concrete Payment shape.
