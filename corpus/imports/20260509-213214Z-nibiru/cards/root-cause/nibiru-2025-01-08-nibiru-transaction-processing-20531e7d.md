# Root-Cause Card

## Metadata

- ID: `nibiru-2025-01-08-nibiru-transaction-processing-20531e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-amount based burn invariant`

## Violated Invariant

- Invariant: When converting a bridge representation, the native-side burn or debit must match the user-supplied amount accepted by the protocol, not a post-transfer amount that a malicious token can reduce.

## Trust Boundary

- Boundary: User-controlled ERC20 transfer semantics cross into native bank burn accounting.

## Attack Surface

- Entrypoint type: FunToken conversion from bank coin to ERC20-origin token
- Sensitive sink: bank coin burn amount and supply accounting

## Impact Pattern

- Primary impact: supply accounting drift
- Secondary impact: possible inflation of native representation

## Short Reusable Lesson

- A conversion path burned native bank representation based on a token-reported received amount instead of the original input amount, allowing fee-on-transfer behavior to skew supply accounting.
