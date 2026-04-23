# Code-Shape Card

## Metadata

- ID: `reth-2023-12-23-reth-transaction-processing-8fb6ed9cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fork-gating`

## Code Shape Summary

- The patch corrects the hardfork check used in the `Transaction::Eip1559` validation path, changing it from `Berlin` to `London` in a consensus validation function. The evidence supports a protocol-rule mismatch in transaction validation, but it does not establish a concrete security impact beyond incorrect gating.

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
