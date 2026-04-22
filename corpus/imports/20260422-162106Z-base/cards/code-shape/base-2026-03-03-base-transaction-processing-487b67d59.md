# Code-Shape Card

## Metadata

- ID: `base-2026-03-03-base-transaction-processing-487b67d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The shown pre-fix code tracked consumed blob count with `blob_index` but lacked a final exact-consumption validation, so a mismatch between consumed blobs and fetched blobs was tolerated instead of being surfaced as an error.

## Search Motifs

- Motif 1: externally supplied structured data is accepted after only partial validation
- Motif 2: one representation is checked while a different reconstructed or cached representation reaches the sink
- Motif 3: exact consumption, identity binding, or state-coordinate consistency is not rechecked before execution

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Add an explicit post-parse invariant check and propagate the failure through typed error paths.

## False Match Warnings

- What looks similar but is often not a bug: The diff supports an integrity hardening interpretation in a consensus-sensitive path, not proof of a concrete exploitable vulnerability.
