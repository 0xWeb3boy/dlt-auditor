# Root-Cause Card

## Metadata

- ID: `rippled-2018-08-10-rippled-access-control-38c3a46a3`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
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

- Primary impact: privilege-misuse
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch is a confirmed security fix for rippled RPC transaction signing. It adds a default access-control gate to sign, sign_for, and the submit path used for sign-and-submit behavior, rejecting non-admin callers unless signing support is explicitly enabled in configuration.
