# Root-Cause Card

## Metadata

- ID: `reth-2024-04-16-reth-storage-33b195af3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-hash-reconstruction`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- `33b195af3` fixes incorrect reconstruction of sidechain block hashes in `all_chain_hashes`. The patch addresses overlapping parent block numbers and parent blocks beyond the original sidechain tip, and adds a regression test for sidechain hash behavior. The provided evidence supports a correctness bug in blockchain-tree fork handling, but does not establish a confirmed security vulnerability.
