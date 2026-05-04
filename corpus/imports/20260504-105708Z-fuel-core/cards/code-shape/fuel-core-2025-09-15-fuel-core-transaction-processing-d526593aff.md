# Code-Shape Card

## Metadata

- ID: `fuel-core-2025-09-15-fuel-core-transaction-processing-d526593aff`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting-hardening`

## Code Shape Summary

- Complexity expressions combined storage_read and first/page size in the wrong order, charging fixed storage cost plus child work instead of per-item storage plus child work.

## Search Motifs

- first.unwrap_or_default multiplied only by child_complexity
- storage_read added outside pagination multiplier
- GraphQL pagination complexity correction
- query cost constants increased

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Rewrite pagination formulas so page size multiplies both child complexity and storage-read cost, and raise default cost constants to better reflect real work.

## False Match Warnings

- No issue if maximum page size is tiny and separately enforced.
- No issue if the resolver performs constant-time indexed reads regardless of requested item count.
