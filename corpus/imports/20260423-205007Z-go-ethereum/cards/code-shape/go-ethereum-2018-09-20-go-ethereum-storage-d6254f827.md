# Code-Shape Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`

## Code Shape Summary

- The root cause was a random equal-total-difficulty, same-height fork-choice tie-break that did not account for whether the current canonical block was locally mined. This could cause a self-mined canonical block to be replaced by an external competitor solely due to randomness. The evidence does not support classifying this as persisted state corruption or a block validation flaw.

## Search Motifs

- Motif 1: rpc method missing exact checks for fork choice tie break hardening
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Replace random consensus-adjacent tie-break behavior with explicit policy-aware fork-choice logic that can consult local node state, while preserving stronger-chain total-difficulty selection

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Replace random consensus-adjacent tie-break behavior with explicit policy-aware fork-choice logic that can consult local node state, while preserving stronger-chain total-difficulty selection.

## False Match Warnings

- Classify as fork-choice hardening, not a confirmed security fix.
- Do not claim remote exploitability from the supplied patch alone.
