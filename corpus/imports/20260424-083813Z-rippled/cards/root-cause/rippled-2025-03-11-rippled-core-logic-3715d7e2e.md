# Root-Cause Card

## Metadata

- ID: `rippled-2025-03-11-rippled-core-logic-3715d7e2e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: privilege-misuse
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch likely fixes access-control bugs in vault deposit and shared MPToken authorization logic.
