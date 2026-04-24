# Root-Cause Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-949b3639c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-ancestor-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `parent-and-ancestor-validation`

## Violated Invariant

- Invariant: Forkchoice handling should distinguish a head that is already known invalid, or descends from known invalid ancestry, from a head that merely cannot yet be canonicalized due to sync state. Responses on that path should preserve invalid ancestry information instead of treating every canonicalization failure as generic recovery.

## Trust Boundary

- Boundary: forkchoice or sidechain state -> persistent storage provider

## Attack Surface

- Entrypoint type: blockchain-tree/state-provider-path
- Sensitive sink: canonical state view, fork ancestry, or persisted trie updates

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Forkchoice handling should distinguish a head that is already known invalid, or descends from known invalid ancestry, from a head that merely cannot yet be canonicalized due to sync state. Responses on that path should preserve invalid ancestry information instead of treating every canonicalization failure as generic recovery.
