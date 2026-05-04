# Root-Cause Card

## Metadata

- ID: `snarkvm-2022-07-11-snarkvm-cryptography-ac990f3e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-balance-nonnegativity-constraint`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `value-conservation`

## Violated Invariant

- Invariant: A private value-transfer circuit must prove that net record balance cannot be negative, not only that field encodings are algebraically consistent.

## Trust Boundary

- Boundary: transaction witness records -> value-conservation circuit constraints

## Attack Surface

- Entrypoint type: state-transition-circuit
- Sensitive sink: transition proof acceptance for record input/output balance

## Impact Pattern

- Primary impact: economic integrity
- Secondary impact: invalid proof acceptance prevention

## Short Reusable Lesson

- Field equality is not a substitute for signed-domain range checks in value accounting circuits.
