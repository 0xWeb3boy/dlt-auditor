# Code-Shape Card

## Metadata

- ID: `sei-chain-2023-02-03-sei-chain-consensus-562746653`
- Bug family: `staking_registry_and_accountability`
- Bug class: `oracle-validator-slashing-enforcement-bypass`

## Code Shape Summary

- The patch changes oracle slashing so abstentions count against a validator's valid-vote rate. Previously, `SlashAndResetCounters` computed the rate using only `MissCount`, allowing excessive abstentions to avoid the configured slash and jail consequences.

## Search Motifs

- Motif 1: valid rate subtracts MissCount but not AbstainCount
- Motif 2: oracle abstain counter exists outside slashing numerator
- Motif 3: tests expect jailing only for misses

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Include all invalid participation counters in the same threshold calculation and regression-test slash/jail outcomes.

## False Match Warnings

- Abstentions are intentionally exempt by protocol design and documented governance parameters.
- Another path separately penalizes abstentions before validator reset.
