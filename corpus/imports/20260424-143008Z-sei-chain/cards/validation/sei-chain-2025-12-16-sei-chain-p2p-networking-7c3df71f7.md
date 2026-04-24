# Validation Card

## Metadata

- ID: `sei-chain-2025-12-16-sei-chain-p2p-networking-7c3df71f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-peer-resource-abuse-hardening`

## What Confirmed The Issue

- Evidence 1: Default mempool config changes CheckTxErrorBlacklistEnabled from false to true.
- Evidence 2: Default CheckTxErrorThreshold changes from 0 to 50, making the blacklist policy usable by default.

## What Could Have Invalidated It

- Compensating control 1: The failure code reflects user-level invalid transactions rather than peer abuse.
- Compensating control 2: Eviction would let attackers disconnect honest peers by relaying bad user txs.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The failure code reflects user-level invalid transactions rather than peer abuse.
- Caution 2: Eviction would let attackers disconnect honest peers by relaying bad user txs.
