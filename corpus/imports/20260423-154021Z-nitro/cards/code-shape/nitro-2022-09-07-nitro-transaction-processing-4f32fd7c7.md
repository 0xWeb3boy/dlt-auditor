# Code-Shape Card

## Metadata

- ID: `nitro-2022-09-07-nitro-transaction-processing-4f32fd7c7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `message-integrity-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: The strongest supported reading is protocol-integrity hardening in the broadcast-feed path, not a confirmed vulnerability fix. The patch adds explicit contiguous-sequence checks during broadcast ingestion and removes a `RequestId` condition so outbound messages are signed whenever a signer exists.

## Search Motifs

- Motif 1: stream processors append feed items without contiguous sequence checks
- Motif 2: signature behavior depends on a field like RequestId instead of the feed policy itself
- Motif 3: ingest and emit paths enforce different integrity rules for the same message family

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Tighten adjacent protocol-integrity checks by adding explicit sequence validation on ingest and making signing behavior uniform on emission.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
