# Prompt Family: Gas Maturity And Claim Curve Lifecycle

## Use This For

- Time/seconds-based gas maturity counters, claim-rate curves, saved balances, and packed economic state.
- Claim-all helpers, minimum-rate claims, withdrawals, redeposits, resets, and maximum/cap behavior.
- Resource accumulators that can be carried across balance, owner, or mode transitions.

## Prompt

```text
Hunt for gas maturity and claim-curve lifecycle bugs in a blockchain or DLT codebase.

Focus on counters that accrue over time, seconds, blocks, epochs, balances, shares, claim rates, reward rates, or fee balances. Treat these counters as state machines, not as generic arithmetic.

Search patterns:
- accumulated time, seconds, points, or gas-credit counters continue increasing after the economic cap has already been reached
- balance withdrawal, mode change, ownership change, or configuration change leaves saved maturity counters behind for a later redeposit or transfer
- a claim-all helper chooses a locally convenient claim rate instead of the economically optimal point along a piecewise curve
- minimum-rate or maximum-rate claims skip intermediate ranges where the user or protocol should claim more value
- packed timestamp/counter/balance state is updated by one path but not another equivalent path
- zero balance, dust balance, or temporarily withdrawn balance keeps accruing or preserving eligibility for later large claims
- claim/redeem helpers rely on monotonicity when the curve has cliffs, caps, plateaus, rounding discontinuities, or time-dependent thresholds
- cross-language mirrors of the same packed gas state use different field widths, rounding, timestamp units, or overflow behavior
- admin/keeper claims, user claims, claim-on-behalf, claim-all, claim-max, and minimum-rate claims use different formulas for the same economic relation
- simulation or read paths report claimable value from a different counter snapshot than the live claim sink uses

Questions to answer:
1. What exactly matures over time, and what event should stop or reset that maturity?
2. If the principal balance leaves, should accumulated time or seconds leave, reset, or stay with the account?
3. Is the cap enforced during accrual, claim, withdrawal, and redeposit?
4. Does the claim-all path search the whole curve or just choose an endpoint?
5. Are dust, zero, maxed-out, and freshly reset states covered by tests?
6. Do all claim variants use the same packed state and update it atomically?
7. Can a user cheaply preserve maturity, then later attach it to a larger balance or expensive operation?

Severity guidance:
- High if accumulated maturity can be used to underpay block resources, create long-lived denial of service, or drain protocol/developer fees.
- Medium if users can extract extra claims, grief claim recipients, or bypass intended waiting periods.
- Low if the issue is only suboptimal claiming without attacker profit or resource exhaustion.
```
