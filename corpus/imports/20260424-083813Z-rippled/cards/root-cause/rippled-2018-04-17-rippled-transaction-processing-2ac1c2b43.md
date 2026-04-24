# Root-Cause Card

## Metadata

- ID: `rippled-2018-04-17-rippled-transaction-processing-2ac1c2b43`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fee-accounting-invariant`
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

- Primary impact: fee-overcharge-prevention, ledger-integrity
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The patch is best classified as security hardening for rippled's transaction fee and XRP supply invariant checks.
