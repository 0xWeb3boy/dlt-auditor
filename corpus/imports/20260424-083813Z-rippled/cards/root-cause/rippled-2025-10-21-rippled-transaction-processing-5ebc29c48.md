# Root-Cause Card

## Metadata

- ID: `rippled-2025-10-21-rippled-transaction-processing-5ebc29c48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `reserve-enforcement`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: state-accounting, resource-consumption
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The patch fixes VaultWithdraw handling for non-native self-withdrawals that can create a new holding object.
