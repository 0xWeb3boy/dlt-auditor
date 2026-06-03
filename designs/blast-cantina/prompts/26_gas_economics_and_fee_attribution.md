# Prompt Family: Gas Economics And Fee Attribution

## Use This For

- Gas, refund, discount, access-list, intrinsic-cost, precompile, or custom fee bugs.
- Incorrect attribution of fees, penalties, or refunds across users, contracts, sequencers, relayers, or fee recipients.
- Divergence between estimation, simulation, mempool admission, and final execution gas behavior.

## Prompt

```text
Hunt for gas-economics and fee-attribution bugs in a blockchain or DLT codebase.

Focus on code that computes gas used, gas remaining, intrinsic cost, access-list warm/cold state, refunds, discounts, precompile cost, storage write cost, bridge message gas, penalties, or the final fee recipient.

Search patterns:
- precompile or host-call RequiredGas paths where valid and invalid selectors, malformed calldata, fallback selectors, revert classification, and out-of-gas classification charge different amounts for comparable work
- gas meters swapped, copied, wrapped, or reset across precompile calls, system contract calls, bridge message execution, callbacks, refunds, or temporary contexts
- discounts, rebates, fee caps, or free-gas allowances applied globally when the economic rule is per-contract, per-account, per-selector, per-source-chain, or per-message
- gas refunded, credited, or charged to the wrong actor after nested calls, bridge relays, relayed transactions, sponsored calls, or system-account execution
- access-list, warm/cold state, storage refund, or precompile-cost rules reconstructed separately in estimation, simulation, RPC tracing, admission, and final execution
- post-call cleanup, event logging, state writes, nonce updates, maturity counters, or journal operations performed after the code checks that enough gas was reserved
- errors nested in processed, reverted, skipped, relayed, simulated, or prechecked variants where gas exhaustion, expected revert, and unexpected internal failure receive different fee treatment
- fee and gas accounting that uses requested amount, forwarded gas, parent gas limit, or original transaction gas instead of the authoritative consumed amount after the sink returns
- per-block, per-contract, or per-recipient gas counters updated only on success, only on revert, or only on direct calls while equivalent indirect calls consume the same resource
- fee-recipient or coinbase attribution that changes between L1/L2, native/VM, precompile/system-contract, retry, replay, or bridge execution paths

Questions to answer:
1. What gas or fee dimension is being measured, and who is supposed to pay or receive it?
2. Which layer is authoritative for final consumed gas and remaining gas after a nested subsystem returns?
3. Are valid, invalid, reverted, out-of-gas, and malformed-call paths charged consistently with the protocol's economic intent?
4. Are discounts, refunds, and access-list effects scoped to the exact contract, selector, account, or message that earned them?
5. Does simulation or estimation use the same gas path as live execution, including post-call writes and cleanup?
6. Are fee-recipient, refund-recipient, and penalty-recipient fields recomputed from current execution context at the sink?
7. Can an attacker make expensive work execute in a branch classified as free, discounted, refunded, or paid by another actor?

Severity guidance:
- High if the issue enables unbounded free execution, systematic fee theft, bridge relay insolvency, or consensus-visible gas/state divergence.
- Medium if it enables meaningful undercharging, wrong-recipient value flow, or exploitable estimation/admission mismatch.
- Low if the issue is limited to non-consensus diagnostics or conservative overcharging with no value redirection.
```
