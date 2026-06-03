# Prompt Family: Lido Oracle Cap And Maker Shutdown

## Use This For

- Lido/stETH oracle caps, bunker mode, withdrawal queue finalization, large slashing, pending/claimable exits, and delayed loss realization.
- Maker DSR/DAI savings adapters, `DsrManager`, `Pot`, cage/emergency shutdown, paused joins/exits, and recovery ownership.

## Prompt

```text
Hunt for named external-provider emergency-mode bugs in Lido and Maker integrations.

For Lido:
- trace deposited stETH/ETH principal, share accounting, withdrawal requests, finalized/claimable exits, oracle reports, bunker mode, and maximum negative rebase/oracle caps
- compare local withdrawal discounts against externally knowable slashing before and after the Lido oracle is allowed to report the full loss
- check whether pending or claimable withdrawals remain valued at par while the actual claim amount is capped, delayed, or loss-adjusted
- model users exiting before the local accounting catches up to a capped oracle report

For Maker/DSR:
- trace DAI ownership through `DsrManager`, `Pot`, join/exit functions, wards/admins, and emergency shutdown/cage flows
- identify who owns the DAI or pie/chai-like accounting during normal operation and after shutdown
- check whether the adapter can exit without the normal DSR path, and whether protocol/admin/users can recover the asset if Maker disables joins/exits or changes redemption flow
- compare local accounting assumptions during shutdown against actual recoverability of underlying DAI

Search patterns:
- Lido oracle caps or bunker delays understate a large slashing event, allowing withdrawals at an overvalued local price
- a provider queue finalizes or becomes claimable below par while the local manager still counts it at par
- Maker emergency shutdown disables the normal DSR exit path and leaves DAI controlled by an external manager that the protocol cannot recover from
- shutdown/cage state makes local balances appear solvent even though the adapter cannot withdraw or redeem
- admin-only provider reports can be ordered around public emergency events to transfer losses between cohorts

Questions to answer:
1. What external emergency states are represented locally, and what states are ignored?
2. Does the local accounting apply provider oracle caps before letting users withdraw?
3. Can a user exit at a stale/par price after a loss is externally knowable but locally capped?
4. During Maker shutdown, which contract holds the recoverable asset and who can call the needed recovery function?
5. Are provider-specific tests present for large slashing, bunker mode, cage, shutdown, and recovery?

Severity guidance:
- Medium if stale oracle caps or shutdown states let users underpay losses, overwithdraw, or strand recoverable assets.
- Low if only admin sequencing can avoid a bounded operational loss and all assets remain recoverable.
- Informational if the provider integration never uses the affected emergency path.
```
