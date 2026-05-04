# Code-Shape Card

## Metadata

- ID: `snarkvm-2022-08-05-snarkvm-cryptography-18c2a7bdd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fail-open-ledger-lookup`

## Code Shape Summary

- A match arm collapsed `Err(_)` and `Ok(false)` into the same unspent classification, so uncertainty was treated as absence.

## Search Motifs

- contains_serial_number result matched with `_ => commitment`
- ledger lookup error treated the same as not found
- unspent filter returns records on storage errors

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `fail-closed-error-handling`.

## Patch Pattern

- Split success and error arms, return unspent only on `Ok(false)`, and log or drop records on lookup errors.

## False Match Warnings

- The result is informational only and never used for signing or spending decisions.
- A later mandatory consensus check rejects spent records regardless of scanner output.
- Errors are impossible because the data source is an in-memory total map.
