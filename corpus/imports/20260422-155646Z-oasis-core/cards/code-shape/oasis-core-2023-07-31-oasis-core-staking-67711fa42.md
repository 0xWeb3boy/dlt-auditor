# Code-Shape Card

## Metadata

- ID: `oasis-core-2023-07-31-oasis-core-staking-67711fa42`
- Bug family: `staking_registry_and_accountability`
- Bug class: `proposer-liveness-accounting-gap`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence shows a liveness-accounting gap in the displayed code paths: proposer timeout handling did not record a missed proposal there, and there was no helper for resolving the selected scheduler directly into committee-member index space. However, the evidence does not prove that this caused an exploitable bypass, mis-slashing, or consensus failure before the patch.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The patch records missed proposals when a valid proposer-timeout transaction is processed, and it adds 'TransactionSchedulerIdx' so scheduler identity can be expressed as a committee-member index instead of only as a position within the filtered worker slice. This makes the new proposer-timeout accounting usable by later liveness evaluation code.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
