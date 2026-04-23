# Code-Shape Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-bug`

## Code Shape Summary

- The patch is best classified as a likely consensus-security fix in go-ethereum core/state. It makes account touch state explicit, journaled, and reversible so zero-value operations on empty accounts interact correctly with EIP158 clearing and Snapshot/Revert behavior. The evidence supports consensus-state compatibility risk, but not claims of theft, cryptographic failure, memory corruption, or proven exploitability.

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
