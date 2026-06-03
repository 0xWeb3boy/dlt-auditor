# Prompt Family: Claim All Saved Seconds And Maturity Extraction

## Use This For

- `claimAll`, claim-rate curves, accumulated seconds, saved seconds, balance withdrawal, redeposit, and maturity caps.
- Piecewise reward curves where an interior point or split strategy can dominate an endpoint helper.
- Resource accumulators that can be made large cheaply and attached to later expensive state.

## Prompt

```text
Hunt for claim-all, saved-seconds, and maturity extraction bugs.

For every gas/reward maturity account, draw the state machine:
- accrual start and stop
- cap
- withdraw/claim/update/reset
- balance zeroing
- redeposit or reconfiguration
- owner/governor changes
- packed timestamp/counter updates

Search patterns:
- `claimAll` claims the full balance at the average maturity even though claiming a smaller amount at a cliff/base/ceil point first yields more
- a helper selects an endpoint but the curve's optimum is an interior point or a split claim
- accumulated seconds remain after the balance is withdrawn, reset, or moved, allowing later redeposit to inherit old maturity
- zero balance or dust balance keeps timestamp/maturity state alive for a later large balance
- maturity caps are enforced at read/claim time but not during accrual, storage, transfer, or mode change
- native geth/client code and Solidity/accounting-contract code update the same packed gas parameters differently
- DoS or resource-exhaustion arises from carrying very large accumulated seconds, not just from claiming extra value

Questions to answer:
1. Does `claimAll` maximize recipient payout, or merely empty the balance using the current average?
2. Can the user do better by claiming exactly enough to reach a base/ceil point, then claiming the remainder?
3. What happens to saved seconds when all balance is withdrawn or set to zero?
4. Can saved seconds be reused with a later balance or by another owner/governor?
5. Are very large accumulated seconds bounded before they reach expensive arithmetic/storage paths?

Severity guidance:
- High if saved maturity can be grown risklessly and later used for resource exhaustion or broad fee drain.
- Medium if claim helpers underpay/overpay materially or allow extractive split strategies.
- Low if only an authorized caller can choose a suboptimal helper and no external party is harmed.
```
