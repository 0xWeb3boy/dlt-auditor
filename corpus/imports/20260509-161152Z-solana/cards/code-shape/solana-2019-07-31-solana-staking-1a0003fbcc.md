# Code-Shape Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-1a0003fbcc`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-withdrawal-epoch-accounting-hardening`

## Code Shape Summary

The patch changes Solana staking epoch accounting behavior. In stake_state.rs, withdraw now rejects a StakeState::Stake account with stake.deactivated == std::u64::MAX before calculating staked balance, and then uses stake.stake(clock.stakers_epoch) instead of stake.stake(clock.epoch). The bank.rs changes shown are tests that query epoch_vote_accounts(epoch) and assert expected stake weights. This may be security relevant because staking and vote weight...

## Search Motifs

- search for stake withdrawal epoch accounting hardening checks near staking entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use the protocol's intended epoch snapshot for stake accounting and add an explicit guard for still-active stake before withdrawal calculations proceed.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
