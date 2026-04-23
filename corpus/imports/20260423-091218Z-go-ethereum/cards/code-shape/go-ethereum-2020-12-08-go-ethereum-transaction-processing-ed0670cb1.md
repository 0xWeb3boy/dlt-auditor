# Code-Shape Card

## Metadata

- ID: `go-ethereum-2020-12-08-go-ethereum-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`

## Code Shape Summary

- The evidence supports replay-protection hardening in go-ethereum contract binding transaction option creation. The patch adds chainID-aware signer construction and routes mobile keyed transaction options and relevant tests through `NewKeyedTransactorWithChainID`. It does not establish an access-control flaw, privilege bypass, or proven exploit.

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
