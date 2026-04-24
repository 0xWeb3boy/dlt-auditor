# Root-Cause Card

## Metadata

- ID: `rippled-2019-03-05-rippled-transaction-processing-c5a938de5`
- Bug family: `authz_and_role_gates`
- Bug class: `regular-key-authorization-hardening`
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

- Primary impact: authorization-integrity, key-management-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch changes transaction authorization and SetRegularKey validation so that, under the fixMasterKeyAsRegularKey amendment, an account cannot set sfRegularKey to the same account ID as sfAccount and master-key disable handling is separated from regular-key authorization.
