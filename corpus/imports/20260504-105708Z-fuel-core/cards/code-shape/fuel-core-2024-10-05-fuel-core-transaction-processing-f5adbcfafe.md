# Code-Shape Card

## Metadata

- ID: `fuel-core-2024-10-05-fuel-core-transaction-processing-f5adbcfafe`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting`

## Code Shape Summary

- Resolver complexity annotations used flat storage costs where block/header/status children could multiply work by selected child complexity.

## Search Motifs

- graphql complexity uses storage_iterator only
- child_complexity omitted from resolver cost
- block_header resolver undercharged
- transaction status block complexity

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Replace flat complexity annotations with formulas that include block/header costs and child_complexity multipliers for nested resolvers.

## False Match Warnings

- No issue if the endpoint is private and separately rate-limited.
- No issue if the resolver ignores child selection or always performs constant work.
