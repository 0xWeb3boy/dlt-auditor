# Code-Shape Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-f694185fe`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The retry/reuse path trusted locally cached checkpoint data without first confirming it against the contract's authoritative historic block-hash mapping.

## Search Motifs

- Motif 1: cache or retry reuse happens without rechecking canonical chain state
- Motif 2: request identity is treated as sufficient even though the historical state coordinate can change
- Motif 3: stale checkpoint, execution, or proof data is reused across parent-context changes

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that an existing request or cache entry matched a local identifier, but did not recheck that the cached state still matched the canonical chain state being acted on.

## Patch Pattern

- What the fix changed structurally: Revalidate cached protocol state against the canonical on-chain source before reusing it in a retry or resume path.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: cached checkpoint reuse is now guarded by validation against contract state before reuse.
