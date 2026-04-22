# Code-Shape Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-1f8f40a6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The proposer flow appears to have treated cached checkpoint data from a prior matching request as reusable authority without first revalidating it against the contract's current canonical historic block-hash mapping.

## Search Motifs

- Motif 1: cache or retry reuse happens without rechecking canonical chain state
- Motif 2: request identity is treated as sufficient even though the historical state coordinate can change
- Motif 3: stale checkpoint, execution, or proof data is reused across parent-context changes

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that an existing request or cache entry matched a local identifier, but did not recheck that the cached state still matched the canonical chain state being acted on.

## Patch Pattern

- What the fix changed structurally: Revalidate cached off-chain state against the current on-chain canonical mapping before reusing it in a consensus-sensitive flow.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the commit hardens a sensitive flow by revalidating cached checkpoint state against on-chain canonical data before reuse.
