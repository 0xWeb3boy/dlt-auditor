# Code-Shape Card

## Metadata

- ID: `reth-2023-02-11-reth-transaction-processing-eba63b8f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-check`

## Code Shape Summary

- Paris activation checks used cumulative total difficulty without consistently passing current block or payload difficulty. The patch expands the predicate inputs across Engine API payload validation, reward logic, and total-difficulty stage validation.

## Search Motifs

- hardfork active_at_ttd called without current difficulty
- transition boundary check differs across engine executor sync paths
- reward or validation behavior keyed only to parent total difficulty

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Expand the fork-activation predicate to include current-block transition data and update every consensus-sensitive call site to use the richer predicate consistently.

## False Match Warnings

- Only relevant near transition boundaries or tests that model them.
- Need the predicate implementation or reproducer to prove the exact failure mode.
- Do not claim post-transition networks are exploitable without boundary reachability.
