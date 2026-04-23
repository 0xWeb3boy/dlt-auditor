# Root-Cause Card

## Metadata

- ID: `go-ethereum-2015-04-29-go-ethereum-storage-4e0796771`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-chain-reorg-invariant`
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

- The patch fixes a chain reorg correctness bug in go-ethereum's core chain manager. Previously, reorg handling depended on comparing the incoming block number with the current canonical head number, which could miss a fork that was ahead and had higher total difficulty. The new logic detects a fork by comparing the canonical predecessor's hash with the incoming block's parent hash. This is plausibly security-relevant because it affects canonical-chain integrity, but the supplied evidence only establishes mixed canonical numbering, not an exploitable vulnerability.
