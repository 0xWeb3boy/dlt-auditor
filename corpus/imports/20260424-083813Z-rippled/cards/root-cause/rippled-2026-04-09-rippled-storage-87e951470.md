# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-09-rippled-storage-87e951470`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: validated ledger/history data -> persistent state or index storage

## Attack Surface

- Entrypoint type: state-storage-or-ledger-update-path
- Sensitive sink: persistent ledger state, object index, cache, or history consistency

## Impact Pattern

- Primary impact: privilege-misuse
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch likely fixes an access-control issue in delegated granular transaction permissions.
