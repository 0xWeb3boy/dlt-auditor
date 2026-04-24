# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-6f86ef9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`

## Code Shape Summary

- Direct checkpoint handling and side-transaction post-handling both need the same range invariant. The patch aligns both paths on exact `EndBlock+1` continuity and makes buffer retrieval errors fail closed.

## Search Motifs

- Motif 1: same checkpoint/range predicate duplicated in message handler and post-consensus handler.
- Motif 2: one path uses exact continuity while another path uses looser overlap prevention.
- Motif 3: `Get*FromBuffer` returns `err` plus existence state and caller ignores the error path.

## Typical Asymmetry

- Multiple admission paths for the same object drift over time; one path may be hardened while another still accepts invalid state.

## Patch Pattern

- Normalize the continuity predicate across all paths and split not-found/existence handling from actual storage errors.

## False Match Warnings

- If the post-handler cannot be reached without a prior exact check, the second change may be defense-in-depth rather than a separate bug.
