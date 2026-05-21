# Prompt Family: Insurance Fresh StETH Front Run Payoff

## Use This For

- Predictable slashing, one-time insurance/backstop events, fresh stETH deposits, old-holder versus new-holder payoff, loss-time eligibility, and L2 rebasing reports.

## Prompt

```text
Hunt for a material fresh-depositor insurance front-run around predictable slashing.

Build a two-cohort payoff model:
- old holders before the provider loss
- fresh stETH depositors after the loss is public/predictable but before local report/insurance accounting
- exact insurance cover
- insurance buffer/residual/over-recovery
- negative-yield discount
- L2 positive rebase/addValue
- final withdrawable value for old and fresh holders

Search patterns:
- fresh depositors receive nominal L2 shares or ETH while the provider asset is already impaired
- one-time insurance cover is applied after fresh depositors are included in current share count or current principal
- exact insurance cover plus stale deposit admission still shifts loss or backing between old and new cohorts
- residual/buffer is small but old-holder loss-shift or fresh-holder dilution is material
- validation kills broad insurance theft because exact cover is netted, but misses a profitable old-holder/fresh-depositor payoff or griefing path

Questions to answer:
1. Can fresh stETH depositors enter after the loss signal but before local report/insurance accounting?
2. Are fresh deposits included in the denominator or share count used to distribute insurance, residuals, or negative yield?
3. Under exact cover, who bears the loss and who receives restored backing?
4. Under no/partial/over cover, what are old-holder and fresh-holder payoffs?
5. Can an attacker profit directly, or is the issue a redistribution from fresh victims to old holders?

Severity guidance:
- Medium if timing lets old holders/fresh depositors materially shift slashing or insurance value across cohorts.
- Low if only tiny residual buffers are affected and exact cover preserves cohort fairness.
- Informational if deposits are paused or loss-time snapshots bind all insurance effects before fresh entrants can join.
```
