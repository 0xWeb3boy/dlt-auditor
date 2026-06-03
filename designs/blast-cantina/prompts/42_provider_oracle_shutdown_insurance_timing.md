# Prompt Family: Provider Oracle Shutdown Insurance Timing

## Use This For

- External yield providers, Lido/stETH, Maker/DSR, oracle caps, slashing, emergency shutdown, insurance, provider removal, pending exits, claimable exits, and keeper/admin sequencing.

## Prompt

```text
Hunt for external-provider oracle, shutdown, and insurance-timing bugs.

For each provider adapter, build a state table:
- deposited principal
- current provider balance
- pending withdrawal requests
- finalized/claimable external exits
- oracle-reported value
- negative yield accumulator
- insurance coverage and eligibility
- emergency shutdown or paused mode
- recovery ownership if the provider path breaks

Search patterns:
- provider pending withdrawals are valued at par even after the external provider has finalized them below nominal
- provider oracle caps, bunker modes, or delayed reports leave balances overstated during large slashing events
- fresh deposits can enter before a predictable loss, rebase, or one-time insurance accounting event and share insurance meant for old holders
- deposits after a loss are minted at par before negative yield is realized, shifting loss to old users or insurance
- emergency shutdown disables the adapter's normal exit path and leaves the underlying asset controlled by an external manager address the protocol cannot recover from
- provider removal/migration snapshots use stale pending balances, skip claimable exits, or reset eligibility
- keeper/admin finalization can occur before mandatory provider claims/reports/insurance withdrawals have incorporated all realized loss

Questions to answer:
1. What external provider states can make the local accounting stale but still apparently valid?
2. Are oracle caps or delayed truth modeled in local share-price math?
3. Are insurance snapshots taken before or after deposits, claims, slashing, and provider reports?
4. Who owns assets during shutdown, and can the protocol recover them without the normal adapter path?
5. Does the finalization sink force all claimable provider exits and realized losses to be incorporated?

Severity guidance:
- Medium if users can enter/exit around loss timing, insurance snapshots, or stale provider accounting to shift value.
- Medium if emergency shutdown can strand provider-held assets without protocol recovery.
- Low if only admin sequencing can avoid a loss and no hostile timing path exists.
```
