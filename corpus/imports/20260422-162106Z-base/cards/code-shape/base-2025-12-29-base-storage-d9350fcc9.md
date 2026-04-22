# Code-Shape Card

## Metadata

- ID: `base-2025-12-29-base-storage-d9350fcc9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-precondition-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The proposer relied on local `game_type` configuration without a runtime check against the authoritative on-chain registry state, so it could continue attempting game creation even when local configuration no longer matched the currently respected type.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: One path read or knew the live runtime policy, but the privileged action could still proceed using local assumptions or an alternate path that did not enforce that policy.

## Patch Pattern

- What the fix changed structurally: Add a runtime precondition check against authoritative on-chain state immediately before a side-effecting operation, and abort when local configuration disagrees with that state.

## False Match Warnings

- What looks similar but is often not a bug: The patch proves a missing runtime validation was added before creating dispute games.
