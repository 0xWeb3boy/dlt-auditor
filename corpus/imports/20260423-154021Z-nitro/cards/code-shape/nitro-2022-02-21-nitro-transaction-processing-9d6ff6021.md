# Code-Shape Card

## Metadata

- ID: `nitro-2022-02-21-nitro-transaction-processing-9d6ff6021`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible patch is best supported as validator correctness hardening. It adds a node-hash consistency check before child traversal and narrows when new-node creation is attempted, but the provided evidence does not establish a concrete vulnerability or a definite security impact.

## Search Motifs

- Motif 1: tree traversal continues after a node-number lookup without checking the returned hash
- Motif 2: branch-selection logic uses partial state matches to continue validation work
- Motif 3: new state nodes are created from references that may be stale after reorgs or races

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Add a fail-fast consistency check and tighten validator branch-selection conditions.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
