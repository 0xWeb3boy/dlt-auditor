# Root-Cause Card

## Metadata

- ID: `rippled-2024-11-05-rippled-core-logic-ec61f5e9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-reserve-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `reserve-enforcement`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: reserve-enforcement, protocol-invariant
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The supported finding is that fixAMMv1_2 adds an amendment-gated reserve check in AMMWithdraw before sending a second withdrawn non-XRP issued asset.
