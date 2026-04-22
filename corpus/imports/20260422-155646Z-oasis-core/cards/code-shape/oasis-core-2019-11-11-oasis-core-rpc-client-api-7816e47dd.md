# Code-Shape Card

## Metadata

- ID: `oasis-core-2019-11-11-oasis-core-rpc-client-api-7816e47dd`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-selection-policy`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible issue is that the entity-level cutoff used in validator election was not represented as its own explicit, validated consensus parameter. Instead, the election path used 'topN', and the patch separates that policy into 'ValidatorEntityThreshold' and requires it to be configured.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The patch introduces 'ValidatorEntityThreshold', stores it in consensus parameters, requires it to be configured during chain initialization, and uses it when limiting the set of stake-ranked entities considered for validator election.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
