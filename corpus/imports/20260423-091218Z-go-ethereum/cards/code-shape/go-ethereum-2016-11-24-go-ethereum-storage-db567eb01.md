# Code-Shape Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-db567eb01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-mismatch`

## Code Shape Summary

- The evidence supports a consensus-relevant StateDB journaling fix, not a broader exploit primitive. The patch adds explicit journaling and undo behavior for touched empty accounts during zero-value balance handling, with a RIPEMD precompile exception described by the commit as Parity compatibility.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
