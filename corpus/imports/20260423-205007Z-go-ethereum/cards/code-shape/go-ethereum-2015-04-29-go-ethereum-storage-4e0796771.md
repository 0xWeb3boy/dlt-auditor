# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-04-29-go-ethereum-storage-4e0796771`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-chain-reorg-invariant`

## Code Shape Summary

- Fork detection was based on relative block height instead of direct parent-link consistency with the current canonical chain. In a split where the higher-total-difficulty fork was ahead of the current head, the old condition could fail to detect that the incoming block belonged to another branch.

## Search Motifs

- Motif 1: transaction validation path missing exact checks for canonical chain reorg invariant
- Motif 2: security-sensitive path reaches canonical-chain selection or persistent chain-state update before rejecting malformed or unauthorized input
- Motif 3: Replace indirect height-based fork detection with direct structural validation of the canonical parent-link relationship before reorg handling proceeds

## Typical Asymmetry

- A small validation gap at an import boundary can influence canonical state, replay behavior, or cross-client consistency.

## Patch Pattern

- Replace indirect height-based fork detection with direct structural validation of the canonical parent-link relationship before reorg handling proceeds.

## False Match Warnings

- Classify as security-hardening rather than confirmed security-fix.
- Limit the claim to canonical chain/reorg invariant enforcement.
