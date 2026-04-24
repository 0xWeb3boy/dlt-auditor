# Validation Card

## Metadata

- ID: `sei-chain-2023-02-03-sei-chain-consensus-562746653`
- Bug family: `staking_registry_and_accountability`
- Bug class: `oracle-validator-slashing-enforcement-bypass`

## What Confirmed The Issue

- Evidence 1: SlashAndResetCounters now subtracts MissCount plus AbstainCount when computing validVoteRate.
- Evidence 2: Tests changed from expecting no slash/no jail for abstaining to expecting bonded-token reduction and jailing.

## What Could Have Invalidated It

- Compensating control 1: Abstentions are intentionally exempt by protocol design and documented governance parameters.
- Compensating control 2: Another path separately penalizes abstentions before validator reset.

## Severity Guidance

- Expected impact band: economic-or-ledger-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Abstentions are intentionally exempt by protocol design and documented governance parameters.
- Caution 2: Another path separately penalizes abstentions before validator reset.
