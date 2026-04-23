# Code-Shape Card

## Metadata

- ID: `go-ethereum-2022-06-29-go-ethereum-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-terminal-block-validation-hardening`

## Code Shape Summary

- The patch fixes a consensus validation gap in go-ethereum's beacon transition header verification. It adds explicit terminal total-difficulty validation for the PoW portion of mixed PoW/PoS header batches and preserves those validation failures during asynchronous result collection.

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
