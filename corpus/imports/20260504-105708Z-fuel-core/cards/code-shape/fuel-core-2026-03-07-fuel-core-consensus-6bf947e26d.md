# Code-Shape Card

## Metadata

- ID: `fuel-core-2026-03-07-fuel-core-consensus-6bf947e26d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-safety`

## Code Shape Summary

- A reconciliation helper swallowed backend read errors and returned an empty list, collapsing three states: no data, read failure, and timeout.

## Search Motifs

- read_stream_entries returns Vec on error
- Redis read failure converted to empty stream
- leader skips committed blocks
- empty vector on timeout in consensus recovery

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Return Result from Redis stream reads, propagate failures through reconciliation, and test that quorum read failures block unsafe leader progress.

## False Match Warnings

- No issue if quorum reconciliation independently requires successful reads.
- No issue if an empty stream cannot authorize production or state advancement.
