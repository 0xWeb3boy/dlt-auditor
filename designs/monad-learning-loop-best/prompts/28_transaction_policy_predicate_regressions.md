# Prompt Family: Transaction Policy Predicate Regressions

## Use This For

- Front-door transaction admission versus proposal, block validation, and execution.
- Fee, balance, reserve, nonce, chain-id, system-sender, EIP-7702 child authorization, and delegated-status mismatches.
- Bugs where an invalid or unpayable transaction is accepted into a hot pool and later causes invalid blocks, empty proposals, repeated timeouts, or free spam.

## Prompt

```text
Hunt specifically for transaction-policy predicate regressions.

Build a table for every transaction type and sub-object:
- legacy
- EIP-2930
- EIP-1559
- EIP-4844, if present
- EIP-7702 parent transaction
- EIP-7702 child authorization tuple
- system/special-sender transactions

For each row, compare these layers:
- JSON-RPC sendRawTransaction admission
- txpool insertion
- txpool forwarding
- replacement or promotion
- tracked/hot pool retention
- proposal sequencing
- block validation
- block-policy coherency
- C++ or final execution validation
- replay/recovery/import

Required checks:
1. Fee formula: compare base fee, max fee, priority fee, legacy gas price, effective gas bid, value, and reserve. Record the exact helper/function and formula used at each layer.
2. Failure disposition: if a transaction fails a later check, record whether it is evicted, demoted, left tracked, retried, selected again, or causes block/vote rejection.
3. EIP-7702 child predicate order: compare recovery, chain id, system/special authority, nonce, low-s, code-state, and authority nonce checks. Record whether a failed child is ignored or makes the parent fatal.
4. Delegated-status timing: compare ordered txpool proposal state to whole-block block-policy summaries. Build a two-transaction witness if a later authorization can change the classification of an earlier transaction.
5. Legacy-vs-typed gas accounting: prove whether legacy transactions are charged full gas price or capped like EIP-1559. Any helper that calls `max_fee_per_gas` and `max_priority_fee_per_gas` must be checked against execution's type-specific gas charge.

High-signal target witness shapes:
- Legacy gas discount: Rust policy computes `gas_limit * min(max_fee, base_fee + priority_fee)` for a legacy transaction where execution charges `gas_limit * gas_price`.
- Wrong-chain system sender: txpool skips an EIP-7702 authorization because the child chain id is wrong before checking that the authority is the system sender, but block validation checks system sender first and rejects the parent/block.
- Base-fee-only affordability: txpool insertion or forwarding only requires balance for `base_fee * gas_limit` or `max_fee >= base_fee`, while proposal/block policy requires full effective bid and leaves failures hot.
- Order-dependent delegated status: txpool proposal evaluates transaction X before transaction Y's EIP-7702 authorization marks the authority delegated, while block policy globally pre-marks the authority from Y and rejects X under reserve/non-emptying rules.

False-positive filters:
- Do not stop at "a later layer validates it"; the issue is retained work, repeated proposal failure, or vote/block rejection after earlier acceptance.
- Do not merge the four witness shapes above. They are separate mechanisms even though all involve transaction policy.
- Do not reject a current-code mechanism solely because docs mention a prior public issue or patch. Only current code-level evidence that the exact predicate is fixed kills the candidate.
- Do not count a generic Rust/C++ EIP-7702 behavior-filter mismatch as the wrong-chain/system-sender bug unless the system sender address and predicate order are explicit.

Output requirements:
- Include a transaction predicate matrix.
- Include at least one concrete candidate or a killed-candidate entry for each high-signal witness shape above.
- For every candidate, include files, functions, exact predicate order, failure disposition, and a minimal attacker sequence.
```
