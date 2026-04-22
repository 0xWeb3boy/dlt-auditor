# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-10-28-oasis-core-staking-a34ab1924`
- Bug family: `staking_registry_and_accountability`
- Bug class: `slashability-bypass`

## Code Shape Summary

- Short description of what the buggy code looked like: Registry cleanup and deregistration rules were too aggressive: node records could be removed on expiration before the staking debonding window ended, and entity removal did not enforce the continued existence of dependent node records.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The registry now keeps expired nodes for the staking debonding interval, prevents entity deregistration when the entity still has registered nodes, hides expired retained nodes from query results, and reuses existing node status when such a node is registered again.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
