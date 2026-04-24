# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-11-13-sei-chain-p2p-networking-f6d7875ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-invalid-peer-accountability`

## Code Shape Summary

- The supported finding is security hardening in p2p reactor error handling. The visible patch replaces several passive error-reporting paths with peer eviction in blocksync, consensus state, consensus vote-set-bits, and statesync invalid light-block handling.

## Search Motifs

- Motif 1: peer error logged but no peerManager.Evict
- Motif 2: invalid light block handled without disconnect
- Motif 3: handler has m.From or resp.peer available but only reports error

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Replace passive reporting with peer eviction or scoring on selected invalid-input paths where peer attribution is reliable.

## False Match Warnings

- The error can be caused by honest network races and eviction would be unsafe.
- Another scoring layer immediately penalizes the same peer.
