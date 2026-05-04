# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-03-22-stellar-core-storage-838f99c3c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trustline-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `centralized-trustline-balance-and-authorization-checks`

## Violated Invariant

- Invariant: All trustline balance changes must pass through a single checked path that enforces limit, nonnegative-balance, and destination authorization constraints.

## Trust Boundary

- Boundary: payment-or-offer-operation -> issued-asset-trustline-state

## Attack Surface

- Entrypoint type: transaction-operation-apply
- Sensitive sink: trustline balance debit, credit, and payment acceptance
- Attacker capability: Submit payments or offer exchanges that credit or debit non-native asset trustlines.
- Main precondition: Multiple operation paths update trustline balance fields directly.

## Impact Pattern

- Primary impact: asset-accounting-integrity
- Secondary impact: authorization-bypass-hardening, ledger-invariant-violation
- Severity guess: medium because Bypassing trustline bounds or authorization can break core issued-asset semantics, though the validation kept this as likely hardening rather than a proven exploit.

## Short Reusable Lesson

- Ledger accounting invariants decay when every operation path hand-rolls balance mutation; put the invariant in the mutation primitive.
