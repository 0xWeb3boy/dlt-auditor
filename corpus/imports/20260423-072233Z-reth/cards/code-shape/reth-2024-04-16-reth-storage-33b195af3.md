# Code-Shape Card

## Metadata

- ID: `reth-2024-04-16-reth-storage-33b195af3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-hash-reconstruction`

## Code Shape Summary

- `33b195af3` fixes incorrect reconstruction of sidechain block hashes in `all_chain_hashes`. The patch addresses overlapping parent block numbers and parent blocks beyond the original sidechain tip, and adds a regression test for sidechain hash behavior. The provided evidence supports a correctness bug in blockchain-tree fork handling, but does not establish a confirmed security vulnerability.

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
