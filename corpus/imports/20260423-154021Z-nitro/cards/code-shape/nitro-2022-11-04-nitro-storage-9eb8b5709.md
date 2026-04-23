# Code-Shape Card

## Metadata

- ID: `nitro-2022-11-04-nitro-storage-9eb8b5709`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preimage-source-mixing`

## Code Shape Summary

- Short description of what the buggy code looked like: The diff shows a consistency hardening change in validator wiring and preimage sourcing, but the provided evidence does not establish a concrete vulnerability. The strongest grounded change is that the stateless preimage resolver stops consulting live trie state via `db.Node(hash)` and the staker path is rewired to use handles owned by `statelessBlockValidator`.

## Search Motifs

- Motif 1: stateless resolvers fall back to live trie or database reads when data is missing
- Motif 2: validator subcomponents can fetch preimages from both local chain state and supplied proof context
- Motif 3: patches remove convenient fallback reads to force a single validation source

## Typical Asymmetry

- What was checked in one path but missing in another: The code treated cached, lazily created, or non-finalized state as if it were authoritative, while later validation or cleanup logic depended on stronger finalized-state guarantees.

## Patch Pattern

- What the fix changed structurally: Remove fallback reads from alternate live state in a supposedly self-contained validation path, and route dependent components through a single owning validator context.

## False Match Warnings

- What looks similar but is often not a bug: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
