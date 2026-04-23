# Code-Shape Card

## Metadata

- ID: `reth-2023-01-13-reth-p2p-networking-5c80bc912`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-validation`

## Code Shape Summary

- Discovery-sourced peers were inserted directly instead of flowing through the fork-id validation path. The patch queues a discovered-node action and admits the peer only when its advertised fork id is absent or compatible.

## Search Motifs

- discovery handler calls add_peer directly
- fork_id carried but not checked before insertion
- separate validated peer admission path exists but is bypassed

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Route discovery output through the centralized peer-admission state machine and gate insertion on fork-id compatibility immediately before adding the peer.

## False Match Warnings

- Peers with no fork id may be intentionally allowed by protocol policy.
- Invalid discovery metadata is not a full exploit unless it leads to session success or resource exhaustion.
- Handshake-level validation may be a compensating control.
