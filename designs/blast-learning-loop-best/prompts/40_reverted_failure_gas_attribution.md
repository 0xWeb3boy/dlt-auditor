# Prompt Family: Reverted Failure Gas Attribution

## Use This For

- Transaction-level gas trackers, StateDB journals, failed/reverted frames, refunds, claimable gas, callback markets, relayers, paymasters, and victim-paid execution.
- Cases where EVM state reverts but fee attribution, gas tracking, or claimable rewards are finalized outside the reverted journal.

## Prompt

```text
Hunt for reverted and failed transaction gas-attribution bugs.

Compare three timelines:
- EVM StateDB snapshots and journal rollback
- gas tracker allocation and refund counters
- transaction finalization, fee charging, developer-gas allocation, and claimable-gas updates

Search patterns:
- a reverted frame still leaves gas tracker allocations to the reverting contract or callback target
- failed top-level transactions still allocate claimable gas to contracts that deliberately burned gas then reverted
- refund counters are journaled but gas tracker allocations are not, or vice versa
- an attacker-controlled callback can make a victim, marketplace, router, paymaster, wallet, relayer, or signature-check flow pay for failed work
- claimable gas can accrue to the attacker-controlled reverting contract even though no application-level state change happened
- validation rejects the issue as "sender paid" without modeling who induced the sender to pay

Questions to answer:
1. Does the gas tracker revert together with StateDB snapshots, or is it finalized transaction-wide?
2. Which contract address receives claimable gas for failed or reverted work?
3. Who submitted and paid for the transaction in realistic router, callback, signature, and relayer flows?
4. Can an attacker later claim the gas balance attributed to the reverting contract?
5. Do tests cover revert-after-burn, nested revert, failed top-level transaction, and victim-paid callback paths?

Severity guidance:
- Medium if a victim-paid failed transaction can transfer meaningful claimable gas to an attacker-controlled contract.
- Low if only self-paid transactions are possible or the value always goes to the protocol.
- Informational if both state and fee attribution cleanly revert or no attacker-controlled paid path exists.
```
