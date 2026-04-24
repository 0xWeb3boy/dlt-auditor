# Root-Cause Card

## Metadata

- ID: `rippled-2026-01-15-rippled-transaction-processing-c0b671206`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rounding-accounting-yield-theft`
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

- Primary impact: economic-value-theft, accounting-integrity
- Secondary impact: Ledger-state impact scoped to affected accounts, assets, offers, reserves, or delegated permissions.

## Short Reusable Lesson

- Likely security fix in rippled's lending LoanPay path. The strongest evidence is the commit message saying a new test covers "Yield Theft via Rounding Manipulation" and now verifies no yield theft occurs, together with changes around rounded vault payments, assets-available/assets-total checks, and funds-conservation checks in LoanPay.cpp.
