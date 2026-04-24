# Root-Cause Card

## Metadata

- ID: `rippled-2013-01-19-rippled-transaction-processing-308ca21b9`
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

- Primary impact: state-accounting, economic-policy-bypass
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The grounded substantive fix is in WalletAdd: it changes an account-creation XRP send from a simple balance-versus-amount check to a reserve-aware funding check.
