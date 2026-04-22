# Code-Shape Card

## Metadata

- ID: `scroll-2025-09-29-scroll-transaction-processing-09ef1ddb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-input-selection`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a validium-specific correctness fix in how the watcher sources L1 message transactions before later processing. It does not, by itself, establish a vulnerability, exploit path, or concrete security impact, so the strongest justified classification is unclear rather than confirmed security.

## Search Motifs

- Motif 1: watcher re-queries transactions instead of consuming the transaction list already attached to the block
- Motif 2: validium-specific path selects auxiliary data source rather than canonical observed input
- Motif 3: patch introduces local blockTxs variable or original transaction source comment before later message processing

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Thread the authoritative transaction set from the observed block through validium watcher processing instead of reconstructing message inputs from an alternate source.

## False Match Warnings

- Warning 1: If the alternate query path is guaranteed to return the exact same canonical transactions in the same order, a similar refactor may be less meaningful.
- Warning 2: The interesting signal is not variable renaming but the move to the authoritative transaction source for subsequent processing.
- Warning 3: The evidence supports watcher integrity hardening, not a demonstrated bridge exploit.
