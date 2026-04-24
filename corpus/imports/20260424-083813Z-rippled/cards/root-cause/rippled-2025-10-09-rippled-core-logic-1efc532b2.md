# Root-Cause Card

## Metadata

- ID: `rippled-2025-10-09-rippled-core-logic-1efc532b2`
- Bug family: `authz_and_role_gates`
- Bug class: `receiver-authorization-hardening`
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

- Primary impact: authorization-policy-enforcement, asset-transfer-eligibility
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The provided evidence shows changes in LoanSet and LoanPay around amortization validation, borrower holding creation, vault receipt authorization, and broker-fee routing when freeze/deep-freeze state affects the intended receiver.
