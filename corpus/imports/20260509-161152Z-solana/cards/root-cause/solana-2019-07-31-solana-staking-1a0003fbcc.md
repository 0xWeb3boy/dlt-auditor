# Root-Cause Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-1a0003fbcc`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-withdrawal-epoch-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-accountability-invariant`

## Violated Invariant

- Protocol input must satisfy stake accountability invariant before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The grounded root cause is an epoch-basis mismatch or incomplete guard in staking accounting: the old shown code used clock.epoch for the withdrawal staked-balance calculation, while the fixed code uses clock.stakers_epoch and explicitly rejects still-activated stake. The evidence does not establish that this mismatch allowed a security breach.

## Impact Pattern

- Primary impact: stake-accounting-integrity, withdrawal-policy-enforcement
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes Solana staking epoch accounting behavior. In stake_state.rs, withdraw now rejects a StakeState::Stake account with stake.deactivated == std::u64::MAX before calculating staked balance, and then uses stake.stake(clock.stakers_epoch) instead of stake.stake(clock.epoch). The bank.rs changes shown are tests that query epoch_vote_accounts(epoch) and assert expected stake weights. This may be security relevant because staking and vote weight...
