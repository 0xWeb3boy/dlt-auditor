# Root-Cause Card

## Metadata

- ID: `rippled-2024-04-22-rippled-core-logic-3f7ce939c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `amm-rounding-invariant-hardening`
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

- Primary impact: protocol-accounting-integrity, economic-invariant-preservation
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- The provided evidence supports a likely security-relevant AMM accounting fix. The commit states that swap rounding could sometimes violate the AMM balance-product invariant by very small amounts and introduces the fixAMMRounding amendment so rounding favors the AMM.
