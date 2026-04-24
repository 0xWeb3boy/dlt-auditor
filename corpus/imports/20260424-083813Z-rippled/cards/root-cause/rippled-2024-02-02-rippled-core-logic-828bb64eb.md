# Root-Cause Card

## Metadata

- ID: `rippled-2024-02-02-rippled-core-logic-828bb64eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`
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

- Primary impact: state-accounting, economic-distortion
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The evidence supports a protocol reserve-enforcement fix in rippled's NFTokenAcceptOffer sell-offer path.
