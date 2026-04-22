# Code-Shape Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-9cd40e7d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The decision logic in the challenger used validation results for all intermediate roots rather than the single root referenced by the on-chain challenge. That incorrect scope allowed unrelated invalid roots to influence the nullification decision.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: The generic challenge machinery was present, but the branch for the specific challenged proof, root, or fallback transition reused the wrong validation rule or dropped the needed state.

## Patch Pattern

- What the fix changed structurally: Replace broad heuristic validation over a collection with validation scoped to the exact indexed item that the protocol action references.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the old challenger logic could mis-handle fraudulent ZK challenges by consulting unrelated intermediate roots.
