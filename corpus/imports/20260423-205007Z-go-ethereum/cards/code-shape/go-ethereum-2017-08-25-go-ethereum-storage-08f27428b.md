# Code-Shape Card

## Metadata

- ID: `go-ethereum-2017-08-25-go-ethereum-storage-08f27428b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `contract-address-collision`

## Code Shape Summary

- The provided evidence supports a missing pre-creation occupancy check in the EVM CREATE path relative to the Metropolis EIP 684 rule. It does not prove that this omission was exploitable as a vulnerability.

## Search Motifs

- Motif 1: block or header validation path missing exact checks for contract address collision
- Motif 2: security-sensitive path reaches consensus-visible state transition or journal replay before rejecting malformed or unauthorized input
- Motif 3: Add a fail-closed protocol invariant check at the contract-creation boundary before downstream account creation proceeds

## Typical Asymmetry

- A small validation gap at an import boundary can influence canonical state, replay behavior, or cross-client consistency.

## Patch Pattern

- Add a fail-closed protocol invariant check at the contract-creation boundary before downstream account creation proceeds.

## False Match Warnings

- Treat as protocol security hardening, not a proven vulnerability fix.
- Do not claim demonstrated state corruption or storage overwrite from the supplied evidence alone.
