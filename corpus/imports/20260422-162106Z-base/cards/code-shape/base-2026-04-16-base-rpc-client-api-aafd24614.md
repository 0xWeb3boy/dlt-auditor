# Code-Shape Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-aafd24614`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `audit-log-integrity`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence suggests the old design used read-modify-write updates against one shared bundle-history object in S3, which the new comments describe as creating read-modify-write contention. The patch addresses that by making each event an immutable record with write-once semantics, but the excerpts do not prove a specific pre-patch failure beyond that contention risk.

## Search Motifs

- Motif 1: mutable object rewrite used as the source of audit history
- Motif 2: append-only events reconstructed from the latest snapshot instead of immutable entries
- Motif 3: storage writes lack write-once or conditional-create semantics for audit data

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace mutable aggregate-object updates with immutable per-event records, enforce write-once storage for each event key, treat duplicate deliveries as no-ops, and rebuild aggregate history by enumerating stored events.

## False Match Warnings

- What looks similar but is often not a bug: This supports an audit-integrity hardening interpretation, not a confirmed exploitable security vulnerability.
