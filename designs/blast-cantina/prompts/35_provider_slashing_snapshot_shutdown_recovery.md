# Prompt Family: Provider Slashing Snapshot Shutdown Recovery

## Use This For

- Staking/savings providers, slashing, oracle caps, pending withdrawals, insurance snapshots, emergency shutdown, and recovery ownership.
- Publicly predictable provider loss events where deposits, withdrawals, and insurance commits can be ordered adversarially.
- Third-party wrappers such as savings managers that may own the recoverable asset during emergency shutdown.

## Prompt

```text
Hunt for provider slashing, insurance snapshot, shutdown, and recovery bugs.

For each external provider, record:
- who owns the provider position on-chain
- how principal, yield, pending withdrawals, and claimed assets are measured
- how negative yield/slashing is detected and capped
- when insurance is applied and to which cohort
- whether provider shutdown has a special recovery path and who can call it

Search patterns:
- provider oracle caps understate large losses, causing withdrawal share price or insurance math to use a stale/par value
- pending withdrawals are counted at nominal value even though the provider can settle them below nominal after slashing
- a public slashing/shutdown event lets new depositors enter before the loss or insurance snapshot and receive insurance they did not earn
- one-time insurance is distributed to current balances instead of loss-time balances
- bridge deposits of provider tokens are immediately accepted during predictable slashing or shutdown windows
- emergency shutdown disables the normal exit path, and the integration lacks the provider-specific recovery function
- assets are legally/recoverably owned by a wrapper/manager contract that the protocol cannot command during shutdown
- a provider removal or migration path excludes nonzero pending or staked value from aggregate accounting

Questions to answer:
1. Is the loss event predictable before the provider balance/oracle actually updates?
2. What snapshot determines insurance eligibility, and can users deposit or withdraw around it?
3. Are pending withdrawals valued at expected realized value, not nominal request value?
4. Does the provider impose loss-report caps, bunker modes, pauses, cages, shutdowns, or wrapper ownership constraints?
5. Who can recover assets during emergency mode: the protocol manager, an external wrapper, a provider admin, current token holders, or original depositors?

Severity guidance:
- High if slashing/shutdown can cause insolvency, strand protected assets, or let fresh depositors drain insurance.
- Medium if losses are materially misallocated between cohorts or pending withdrawals are under-discounted.
- Low if only a trusted operator can choose a bad migration while all assets remain recoverable.
```
