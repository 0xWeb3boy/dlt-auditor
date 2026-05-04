# Code-Shape Card

## Metadata

- ID: `snarkvm-2022-07-11-snarkvm-cryptography-ac990f3e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-balance-nonnegativity-constraint`

## Code Shape Summary

- Circuit accounting summed inputs and outputs, then checked field equality without also constraining the signed balance to be non-negative.

## Search Motifs

- balance.to_field() equality without an msb or range check
- inputs minus outputs represented in signed integer gadgets
- asset conservation proof lacks non-negative net balance assertion

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `value-conservation`.

## Patch Pattern

- Add an explicit sign-bit or range constraint for non-negativity alongside the existing field-domain consistency check.

## False Match Warnings

- A separate range proof already constrains the signed balance before conversion.
- The code path is only for test parsing and not used in proof generation.
- The transition kind is exempt because value conservation is enforced elsewhere.
