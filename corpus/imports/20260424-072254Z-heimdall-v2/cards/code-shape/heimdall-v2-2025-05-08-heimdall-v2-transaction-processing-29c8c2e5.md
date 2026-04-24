# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-29c8c2e5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`

## Code Shape Summary

- Checkpoint admission compared `lastEnd > newStart`, which rejects overlap but permits gaps. The patch requires `lastEnd + 1 == newStart` and returns on checkpoint-buffer read errors before buffer-dependent processing.

## Search Motifs

- Motif 1: range or checkpoint validation uses `previousEnd > start` as the only continuity check.
- Motif 2: handlers accept `StartBlock`/`EndBlock`, `from`/`to`, epoch ranges, batches, spans, or checkpoints.
- Motif 3: patch adds `+ 1 != start` or an exact successor predicate.

## Typical Asymmetry

- "After the tip" is weaker than "immediately after the tip"; range state machines often need exact successor validation.

## Patch Pattern

- Replace permissive freshness checks with exact continuity checks and treat storage read failures as fatal rather than equivalent to absence.

## False Match Warnings

- Some protocols intentionally allow sparse checkpoints. Confirm whether gaps are expected, proven elsewhere, or rejected by a downstream contract.
