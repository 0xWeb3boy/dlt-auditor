# Code-Shape Card

## Metadata

- ID: `snarkvm-2025-03-05-snarkvm-consensus-204e8b564`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursion-resource-accounting-hardening`

## Code Shape Summary

- Resource checks used cached call-count or finalize-cost data instead of traversing the current call graph during stack initialization.

## Search Motifs

- number_of_calls cache used for recursion limit
- finalize cost cached separately from live cost calculation
- stack initialization inserts functions before validating call expansion

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `recursive-call-bound`.

## Patch Pattern

- Replace cached lookups with live call-graph traversal, centralize cost calculation, and validate maximum calls during stack initialization.

## False Match Warnings

- The cache is immutable and recomputed on every program change.
- A later mandatory execution path enforces the same recursion bound before work is done.
- The call graph is acyclic and bounded by syntax alone.
