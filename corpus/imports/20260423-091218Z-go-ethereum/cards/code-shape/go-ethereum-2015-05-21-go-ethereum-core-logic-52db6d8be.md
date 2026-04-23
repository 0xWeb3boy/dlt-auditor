# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-21-go-ethereum-core-logic-52db6d8be`
- Bug family: `authz_and_role_gates`
- Bug class: `cross-check-validation-bypass`

## Code Shape Summary

- The patch fixes a downloader validation weakness where forged blocks could satisfy cross-checks by pointing their parent hash at any known queued hash. The fix records the expected parent hash with each pending cross-check and requires the returned block to match it exactly.

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
