# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-02-06-oasis-core-staking-635fcfd29`
- Bug family: `staking_registry_and_accountability`
- Bug class: `missing-stake-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: The affected paths previously lacked explicit runtime stake/deposit checks at the shown admission and lifecycle transition points. From the provided evidence alone, it is not proven whether that absence was a vulnerability or simply behavior that this change intentionally tightened.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The patch fetches consensus parameters where needed, gates the behavior on 'DebugBypassStake', invokes 'EnsureSufficientRuntimeStake', and uses the result to reject runtime registration or suspend already-registered runtimes in key manager and roothash flows.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
