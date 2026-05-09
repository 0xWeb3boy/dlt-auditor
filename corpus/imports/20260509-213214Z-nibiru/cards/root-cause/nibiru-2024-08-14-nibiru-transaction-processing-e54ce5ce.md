# Root-Cause Card

## Metadata

- ID: `nibiru-2024-08-14-nibiru-transaction-processing-e54ce5ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `origin-aware supply conservation`

## Violated Invariant

- Invariant: A token bridge must conserve value according to the origin of the mapped asset: returning a wrapped representation should release existing backing or burn representation, not mint new backing supply.

## Trust Boundary

- Boundary: ERC20 token callback/bridge path crosses into native bank mint, burn, and module-account accounting.

## Attack Surface

- Entrypoint type: token bridge precompile conversion from ERC20 representation back to bank coin
- Sensitive sink: bank mint/burn and module-to-user bank transfer

## Impact Pattern

- Primary impact: supply or backing drift
- Secondary impact: possible asset inflation if drift is exploitable

## Short Reusable Lesson

- A bridge conversion path treated all token mappings the same and minted native coins where bank-origin mappings should burn representation and release backing.
