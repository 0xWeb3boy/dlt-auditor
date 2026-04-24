# Validation Card

## Metadata

- ID: `sei-chain-2025-11-13-sei-chain-p2p-networking-f6d7875ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-invalid-peer-accountability`

## What Confirmed The Issue

- Evidence 1: Consensus state-channel handler errors now call router.Evict for the sending peer while the context is active.
- Evidence 2: Consensus vote-set-bits handler errors now evict the sending peer instead of only sending a peer error.

## What Could Have Invalidated It

- Compensating control 1: The error can be caused by honest network races and eviction would be unsafe.
- Compensating control 2: Another scoring layer immediately penalizes the same peer.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The error can be caused by honest network races and eviction would be unsafe.
- Caution 2: Another scoring layer immediately penalizes the same peer.
