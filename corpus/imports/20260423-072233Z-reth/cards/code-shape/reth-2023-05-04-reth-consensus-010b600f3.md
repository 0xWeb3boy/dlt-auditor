# Code-Shape Card

## Metadata

- ID: `reth-2023-05-04-reth-consensus-010b600f3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`

## Code Shape Summary

- The patch adds an explicit consistency check in block insertion so a block is rejected when its `parent_hash` matches a canonical block but the canonical height of that hash does not equal the claimed parent number. The evidence supports that this is a consensus-sensitive invariant check, but it does not establish a concrete vulnerability or exploit path.

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
