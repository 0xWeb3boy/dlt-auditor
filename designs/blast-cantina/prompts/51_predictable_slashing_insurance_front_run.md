# Prompt Family: Predictable Slashing Insurance Front Run

## Use This For

- Insurance/backstop funds, Lido/stETH slashing, negative yield reports, public loss events, deposits before reports, loss-time snapshots, and current-holder rebase distribution.

## Prompt

```text
Hunt for one-time insurance or backstop funds that can be captured or diluted by fresh deposits before predictable slashing is accounted.

Build a timeline:
- external loss/slashing becomes public or predictable
- provider oracle/report or claim has not yet updated local accounting
- users can still deposit or bridge into the rebasing/share system
- insurance withdrawal or coverage amount is selected
- negative yield, insurance recovery, and L2 rebase/share-price update are reported
- users withdraw after insurance/rebase state changes

Search patterns:
- new depositors mint shares at a stale pre-loss price after a loss is public but before a negative-yield/insurance report
- insurance eligibility is current-balance based instead of loss-time balance based
- insurance cover is applied once and then distributed through current rebasing shares
- L1 deposits cannot be paused or are ordered before the yield report deposit to L2
- recovery buffers or exact cover amounts are not bound to users who were exposed during the loss interval
- admin/keeper report sequencing is predictable enough for fresh depositors to enter before the insurance event

Questions to answer:
1. Can fresh users enter after the external loss signal but before local accounting or insurance reporting?
2. Are those fresh shares included in the insurance/recovery distribution?
3. Are loss-time balances snapshotted anywhere, or is current share count used?
4. Can deposit and report messages be ordered adversarially across L1/L2?
5. Does exact insurance cover, buffer residual, or over-recovery change who absorbs the loss?

Severity guidance:
- Medium if fresh entrants can capture insurance/backstop value or dilute loss-time holders during a predictable slashing event.
- Low if only admin over-recovery residuals are affected and exact loss cover is snapshot/bound correctly.
- Informational if deposits are paused or loss-time snapshots fully bind insurance eligibility before users can react.
```
