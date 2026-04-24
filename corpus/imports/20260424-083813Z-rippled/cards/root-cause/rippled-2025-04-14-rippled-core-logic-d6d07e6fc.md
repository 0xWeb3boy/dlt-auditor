# Root-Cause Card

## Metadata

- ID: `rippled-2025-04-14-rippled-core-logic-d6d07e6fc`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-correctness`
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

- Primary impact: authorization-enforcement
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- Likely access-control fix in rippled vault deposit authorization. The patch changes VaultDeposit private-vault handling to read the share MPTokenIssuance, use its DomainID metadata for authorization decisions, and add an apply-time MPTokenAuthorize call for private vault shares.
