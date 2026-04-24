# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-02-rippled-access-control-111edef28`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `accounting-integrity`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: ledger-integrity, protocol-accounting-integrity
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The supported finding is a lending LoanBroker accounting-invariant hardening, not an access-control flaw or proven funds-theft vulnerability.
