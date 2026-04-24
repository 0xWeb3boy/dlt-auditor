# Code-Shape Card

## Metadata

- ID: `sui-2022-01-25-sui-transaction-processing-f95e29b749`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-certificate-comparison-semantics`

## Code Shape Summary

- The patch removes generic equality and hashing support from CertifiedOrder and from structs that embed it, because comparing or hashing certificates by their concrete signature sets can encode misleading certificate identity semantics.

## Search Motifs

- input-validation enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Remove misleading generic equality and hashing implementations from certificate-bearing types when structural fields do not safely represent protocol identity.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
