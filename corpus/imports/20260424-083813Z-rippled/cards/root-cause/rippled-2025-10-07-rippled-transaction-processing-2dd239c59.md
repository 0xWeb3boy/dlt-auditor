# Root-Cause Card

## Metadata

- ID: `rippled-2025-10-07-rippled-transaction-processing-2dd239c59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-freeze-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: freeze-restriction-bypass
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The best-supported security finding is incomplete deep-freeze validation in LoanPay::preclaim.
