# Code-Shape Card

## Metadata

- ID: `base-2025-12-29-base-storage-55893ad15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-policy-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The proposer creation path relied on locally configured game type without consulting the live onchain policy source that defines the currently respected type. The surrounding config and ABI plumbing also did not yet expose the registry query needed to enforce that check in this path.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: One path read or knew the live runtime policy, but the privileged action could still proceed using local assumptions or an alternate path that did not enforce that policy.

## Patch Pattern

- What the fix changed structurally: Add an explicit live-policy validation immediately before a sensitive action, and wire the policy source through config and ABI layers so the component can fail closed when local configuration diverges from current protocol policy.

## False Match Warnings

- What looks similar but is often not a bug: The evidence supports a missing proposer-side policy validation guard, not `state-corruption` or a storage bug.
