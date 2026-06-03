# Prompt Family: External Provider Loss Oracle Insurance Shutdown

## Use This For

- External yield/staking/savings providers, pending withdrawals, oracle caps, insurance funds, provider removal, migration, emergency shutdown, and recovery.
- Slashing, negative yield, delayed settlement, queued exits, paused withdrawals, and provider insolvency.
- Timing games where public loss events, deposits, withdrawals, or insurance eligibility can be ordered adversarially.

## Prompt

```text
Hunt for external-provider loss, oracle, insurance, and shutdown bugs in a blockchain or DLT codebase.

Focus on integrations where protocol accounting depends on a third-party provider's delayed or externally governed state: staking, savings-rate managers, vaults, oracle reports, queued withdrawals, loss insurance, emergency shutdown, provider removal, or migration.

Search patterns:
- pending withdrawals are valued at par while a provider can settle them below par after a loss
- oracle caps limit reported losses, causing share price or withdrawal discounts to understate actual provider loss
- users can deposit after a loss is predictable but before insurance eligibility or share price is snapshotted
- one-time insurance or backstop funds are distributed by current balances rather than balances at the loss-earning snapshot
- provider removal or migration drops nonzero principal, pending withdrawals, unclaimed rewards, queued exits, or obligations from aggregate accounting
- emergency shutdown or paused-provider state prevents exits, claims, joins, or recovery, but the integration keeps assuming normal provider operations
- recovered assets can be claimed by the wrong owner, strategy, manager, admin, or current depositor set
- delayed provider receipts, slashing, negative yield, partial withdrawals, or failed claims are treated as zero-yield success
- bridge or vault withdrawals are finalized before external provider loss and insurance state are settled
- keeper/admin-only paths can be front-run or ordered around public loss events to move value between user cohorts

Questions to answer:
1. Which value is immediate, pending, claimable, insured, slashed, paused, shutdown, or recovered?
2. Does share price include pending provider assets at their realizable value or at nominal/par value?
3. Can oracle caps hide losses from withdrawal discounting or insurance math?
4. Is insurance eligibility based on a snapshot before deposits/withdrawals can react to a public loss event?
5. What happens if the provider pauses, slashes, shuts down, delays exits, returns less, or requires a special recovery path?
6. Can an owner/admin migration or provider removal change aggregate accounting while obligations remain?
7. Are recovered assets owned by the original depositors, current token holders, insurance fund, protocol, or provider manager?

Severity guidance:
- High if users can withdraw more than their fair share, new users can capture old-user insurance, or shutdown/recovery can permanently strand protected principal.
- Medium if losses can be misallocated between cohorts, pending operations can be under-discounted, or admin/provider failures can leak value.
- Low if it is only an acknowledged third-party insolvency risk and the protocol's local accounting remains correct.
```
