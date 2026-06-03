# Prompt Family: Bridge Message Gas Replay And Discounted Value

## Use This For

- Cross-domain deposits, withdrawals, retryable messages, finalizers, and relays.
- Minimum gas, forwarded gas, reserve gas, post-call cleanup, replay guards, and nonce/message identity bugs.
- Value conversions, discounts, fees, rounding, and token/native amount mismatches across domains.

## Prompt

```text
Hunt for bridge-message gas, replay, and discounted-value bugs in a blockchain or DLT codebase.

Focus on paths that receive, prove, relay, replay, finalize, or retry messages between chains or between native and VM execution layers.

Search patterns:
- minimum gas validated at deposit time but forwarded gas reduced by base costs, reserve gas, calldata overhead, post-call storage writes, callbacks, or dynamic cleanup
- replay guards keyed by nonce, hash, sender, target, amount, block, or domain but missing one coordinate needed to distinguish equivalent messages
- failed or reverted relay paths that consume or restore replay state inconsistently with fee, refund, retry, or withdrawal state
- direct deposit, system deposit, retry, replay, forced inclusion, and finalization paths that disagree on gas limit, value, sender aliasing, target address, or failure semantics
- cross-domain value conversions where requested amount, nominal amount, discounted amount, rounded amount, minted amount, burned amount, escrowed amount, and calldata amount can differ
- bridge logic that applies discounts or fees before converting units on one path and after converting units on another path
- message execution that writes replay status before ensuring the downstream call and all required post-call writes have enough gas to finish
- sender, origin, target, or chain/domain binding reconstructed from calldata, logs, proofs, or helper output instead of the authenticated message object at the sink
- L1/L2 fee, gas, or value formulas copied across direct and indirect bridge paths without rechecking who pays, who receives, and which side owns rounding dust
- bridge handlers that classify malformed messages, unknown selectors, paused targets, or insufficient gas as successful no-ops while still mutating replay or accounting state

Questions to answer:
1. What is the unique identity of a message, and does every replay guard use all required coordinates?
2. Is minimum gas checked against the true execution budget after base cost, reserve cost, forwarding rules, and post-call writes?
3. Do failed, reverted, and out-of-gas executions advance replay state, refund state, and retry eligibility exactly as intended?
4. Which amount is authoritative on each side: requested, received, escrowed, burned, minted, rounded, discounted, or delivered?
5. Are value conversions and discounts monotonic and applied in the same order across equivalent bridge paths?
6. Can a caller choose target, calldata, gas, value, or replay timing to make one domain commit state while the other domain does not?
7. Are direct deposits, forced messages, retries, and finalized withdrawals compared against one another rather than reviewed in isolation?

Severity guidance:
- High if a bug can duplicate withdrawals, bypass replay protection, mint/withdraw excess value, or permanently break settlement for honest users.
- Medium if it causes meaningful stuck funds, underfunded relays, unfair fee/value rounding, or inconsistent retry/failure semantics.
- Low if it is only a diagnostic, conservative overpayment, or admin-only recovery issue with no user-controlled exploit path.
```
