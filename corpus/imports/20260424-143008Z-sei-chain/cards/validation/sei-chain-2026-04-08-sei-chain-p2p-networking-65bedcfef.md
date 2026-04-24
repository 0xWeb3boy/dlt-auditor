# Validation Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-p2p-networking-65bedcfef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-abuse-accounting-hardening`

## What Confirmed The Issue

- Evidence 1: Reactor handles p2p mempool messages and calls accountFailedCheckTx with m.From after CheckTx errors.
- Evidence 2: accountFailedCheckTx is gated by CheckTxErrorBlacklistEnabled and only counts ErrTxTooLarge or ErrPreCheck errors.

## What Could Have Invalidated It

- Compensating control 1: Counters are purely diagnostic and never affect peer treatment.
- Compensating control 2: A separate peer manager expires all counters reliably.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Counters are purely diagnostic and never affect peer treatment.
- Caution 2: A separate peer manager expires all counters reliably.
