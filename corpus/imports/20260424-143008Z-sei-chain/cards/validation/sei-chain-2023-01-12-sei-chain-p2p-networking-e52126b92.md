# Validation Card

## Metadata

- ID: `sei-chain-2023-01-12-sei-chain-p2p-networking-e52126b92`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-invalid-tx-peer-abuse-hardening`

## What Confirmed The Issue

- Evidence 1: Adds CheckTxErrorBlacklistEnabled and CheckTxErrorThreshold to mempool configuration.
- Evidence 2: Counts failed CheckTx responses per SenderNodeID and calls peerManager.Errored when the enabled threshold is exceeded.

## What Could Have Invalidated It

- Compensating control 1: Invalid submissions are already rate-limited or disconnected at the transport layer.
- Compensating control 2: Failures are ordinary user transaction errors that should not punish relaying peers.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Invalid submissions are already rate-limited or disconnected at the transport layer.
- Caution 2: Failures are ordinary user transaction errors that should not punish relaying peers.
