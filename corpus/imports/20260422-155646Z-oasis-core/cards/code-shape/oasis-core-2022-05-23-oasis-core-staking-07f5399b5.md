# Code-Shape Card

## Metadata

- ID: `oasis-core-2022-05-23-oasis-core-staking-07f5399b5`
- Bug family: `staking_registry_and_accountability`
- Bug class: `reserved-address-invariant-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: 'staking.BurnAddress' was not handled consistently as a dedicated burn sink. The transfer path could treat it like a normal destination, and sanity checking did not enforce that the burn address remain unused in ledger/genesis state.

## Search Motifs

- Motif 1: stake, slashing, or liveness rule missing on an edge path
- Motif 2: validator or committee accounting uses the wrong role coordinate
- Motif 3: reserved or punishable state treated like ordinary state

## Typical Asymmetry

- What was checked in one path but missing in another: Economic or accountability rules existed in the design, but an edge path failed to enforce them for the affected actor, role, or transition.

## Patch Pattern

- What the fix changed structurally: The patch rerouted transfer-to-burn-address operations into shared burn logic via 'burnImpl(...)' and added sanity-check validation that rejects any burn-address ledger entry with non-zero balance or nonce.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
