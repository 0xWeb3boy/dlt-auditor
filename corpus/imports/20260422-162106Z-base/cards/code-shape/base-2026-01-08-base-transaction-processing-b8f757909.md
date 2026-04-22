# Code-Shape Card

## Metadata

- ID: `base-2026-01-08-base-transaction-processing-b8f757909`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `deadline-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: The challenger's local sync logic tied deadline expiry to proposal status instead of to the dispute deadline itself. As a result, expired but still Unchallenged games could be treated as locally challengeable during cache refresh.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: The generic challenge machinery was present, but the branch for the specific challenged proof, root, or fallback transition reused the wrong validation rule or dropped the needed state.

## Patch Pattern

- What the fix changed structurally: Replace a status-gated time check with a direct deadline check at the decision point, then add test-oriented access paths to verify state-sync behavior.

## False Match Warnings

- What looks similar but is often not a bug: Supported: the patch hardens deadline enforcement in off-chain challenger state synchronization.
