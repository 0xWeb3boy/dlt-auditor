# Root-Cause Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-be87dcc68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-target-mismatch`
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

- The patch is a concrete correctness fix for Merkle rebuild checkpoint handling. The provided diff supports that older code could resume from any stored checkpoint, save partial progress without an explicit target at the save site, and leave stale checkpoint metadata around during a rebuild. The evidence does not establish an exploitable vulnerability, remote triggerability, or consensus failure, so this should remain classified as unclear rather than a confirmed security fix.
