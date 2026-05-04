# Code-Shape Card

## Metadata

- ID: `snarkvm-2023-10-07-snarkvm-transaction-processing-289b9edad`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-validation`

## Code Shape Summary

- Deserialization routed mismatched vectors through an infallible `From` constructor instead of rejecting invalid structural combinations.

## Search Motifs

- impl From<(Vec<Request>, Vec<Transition>)> for Authorization
- deserializer reconstructs auth object without length equality
- request and transition arrays are trusted to align by position

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `authorization-structure-validation`.

## Patch Pattern

- Replace infallible construction with `TryFrom`, check vector counts, and route deserialization through the checked constructor.

## False Match Warnings

- Binary deserialization or canonical parsing already rejects mismatched vectors before construction.
- The object is never used until another mandatory verifier checks the same invariant.
- The vectors are produced only by trusted internal code.
