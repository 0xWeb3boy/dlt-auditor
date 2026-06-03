# Prompt Family: Bridge Gas Reserve Fee Discount Upgrade Replay

## Use This For

- Cross-domain bridge deposits/withdrawals, min gas limits, relay reserved gas, L1 data fees, protocol fee-vault balances, discounted withdrawals, and upgrade/replay state.
- Message paths that add post-call storage writes, value conversion, or negative-yield discounts after a base bridge implementation was written.
- Upgrade/reinitialization windows that can reset replay/finalization state.

## Prompt

```text
Hunt for bridge gas reserve, fee discount, and upgrade replay bugs.

For every bridge/message path, compare:
- user-supplied minimum gas
- gas forwarded to the target
- gas reserved for post-call bookkeeping
- added storage writes or events after the target call
- value delivered versus nominal/requested value
- fee charged on L1/L2 data
- replay/failure flags before and after upgrades

Search patterns:
- asset-specific deposits append finalizer work but do not increase `_minGasLimit`
- relay reserved gas constants are stale after adding discounted-value storage writes or extra bookkeeping
- discounted/rounded withdrawals reduce delivered value but not data-fee accounting, protocol-fee accounting, or replay semantics consistently
- fee-vault or protocol-owned balances can be forced through a negative-yield discounted withdrawal path
- failed relay paths assert or revert before writing failure/replay state
- direct and messenger-mediated withdrawals consume provider/queue claims at different points relative to target-call success
- upgrade, reinitializer, or implementation replacement can reset message success/failure flags or replay protections while old messages are pending
- bridge simulation/estimation paths undercount gas because they omit finalizer bookkeeping or provider claims

Questions to answer:
1. Which exact code executes after the target call, and is reserved gas enough for it under the worst discounted/rounded path?
2. Does each direct deposit path include the L2 finalizer gas it actually triggers?
3. Are L1 data fees charged on nominal, discounted, rounded, or delivered values consistently?
4. Can protocol-owned fee balances be withdrawn at a loss or discount by an untrusted caller?
5. Are message replay flags, failed-message flags, and consumed-withdrawal flags preserved across upgrades/reinitializers?

Severity guidance:
- High if funds/messages can be bricked or replay protections can be reset for double execution.
- Medium if users or protocol fee balances are undercharged, over-discounted, or forced through a lossy path.
- Low if only operational gas estimates are imprecise and no funds/messages are at risk.
```
