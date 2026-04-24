# Root-Cause Card

## Metadata

- ID: `rippled-2025-05-05-rippled-transaction-processing-9a8660241`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `accounting-integrity`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: ledger-integrity, state-consistency
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The evidence supports an accounting correctness and invariant-hardening change in rippled's lending loan/vault transaction path.
