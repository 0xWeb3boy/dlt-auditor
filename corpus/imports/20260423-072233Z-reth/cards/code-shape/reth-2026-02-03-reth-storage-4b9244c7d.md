# Code-Shape Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`

## Code Shape Summary

- Storage proof generation could omit root evidence for storage-only or empty-subtrie cases, and pruning could leave reveal metadata stale. The patch forces root-level evidence, emits explicit EmptyRoot markers, and clears revealed paths after pruning.

## Search Motifs

- empty subtrie returns empty proof
- retain_root false drops EmptyRoot evidence
- prune converts nodes to hashes without clearing revealed_paths

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Preserve explicit root or EmptyRoot proof nodes for absence cases and invalidate proof caches whenever pruning changes trie shape.

## False Match Warnings

- A proof-generation bug is not automatically a verifier acceptance bug.
- Local debug proof APIs may not cross a security boundary.
- Need evidence that ambiguous proofs are consumed by trust decisions before claiming exploitability.
