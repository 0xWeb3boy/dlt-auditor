# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-04-22-oasis-core-staking-d477a90f7`
- Bug family: `staking_registry_and_accountability`
- Bug class: `incorrect-validator-voting-power`

## Code Shape Summary

- Short description of what the buggy code looked like: The scheduler election path previously did not assign explicit stake-derived voting power in the shown validator-set construction path; the patch adds that missing mapping.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The fix updates validator election to compute and store per-validator voting power instead of only collecting validator identities. It also introduces a shared scheduler API helper for converting escrowed stake into voting power and initializes the default conversion ratio used by that helper.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
