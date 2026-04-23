# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-04-29-go-ethereum-storage-4e0796771`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-chain-reorg-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: A node's canonical chain numbering should represent one contiguous parent-linked branch selected by total difficulty: for each canonical block at height N, its parent hash should match the canonical block at height N-1. The patch enforces this consistency check more directly during reorg handling, but the provided evidence does not establish a concrete security vulnerability or exploit path.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `canonical-chain selection or persistent chain-state update`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `canonical-chain-integrity`

## Short Reusable Lesson

- The patch fixes a chain reorg correctness bug in go-ethereum's core chain manager.
