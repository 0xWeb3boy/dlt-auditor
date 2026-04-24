# Root-Cause Card

## Metadata

- ID: `rippled-2025-11-14-rippled-core-logic-b195011ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `accounting-integrity`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: under-reserved-ledger-state
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The supported finding is a Vault reserve-accounting fix, not an access-control issue. The patch changes Vault creation from accounting for one owner-reserved object to two, mirrors that on deletion, and adds validation before removing the Vault pseudo-account.
