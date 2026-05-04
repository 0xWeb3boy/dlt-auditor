# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-03-20-stellar-core-storage-cc9a3c0bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trustline-limit-balance-invariant`

## Violated Invariant

- Invariant: A trustline limit update must be rejected if the requested limit is negative or below the balance already held on that trustline.

## Trust Boundary

- Boundary: user-submitted-trustline-operation -> non-native-asset-ledger-entry

## Attack Surface

- Entrypoint type: transaction-operation-apply
- Sensitive sink: trustline limit mutation in ledger storage
- Attacker capability: Submit ChangeTrust-like operations for an existing trustline.
- Main precondition: The existing-trustline branch directly assigns the requested limit.

## Impact Pattern

- Primary impact: asset-accounting-integrity
- Secondary impact: ledger-invariant-violation
- Severity guess: medium because A broken trustline limit invariant can corrupt asset accounting semantics, but the evidence does not show a concrete theft path or consensus split.

## Short Reusable Lesson

- State mutation paths must enforce accounting invariants against both submitted parameters and already-persisted balances.
