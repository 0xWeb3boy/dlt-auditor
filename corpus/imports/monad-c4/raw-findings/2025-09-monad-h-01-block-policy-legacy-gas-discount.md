---
id: monad-c4-2025-09-h-01
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: high
---

## [[H-01] Block policy discounts gas price by incorrectly applying EIP-1559 to legacy transactions](https://code4rena.com/audits/2025-09-monad/submissions/F-81)

*Submitted by [RadiantLabs](https://code4rena.com/audits/2025-09-monad/submissions/S-42), also found by [0x15](https://code4rena.com/audits/2025-09-monad/submissions/S-252) and [0xAsen](https://code4rena.com/audits/2025-09-monad/submissions/S-187)*

`bft/monad-eth-block-policy/src/lib.rs` [#L77](https://github.com/code-423n4/2025-09-monad/blob/5eb99e1c365d61b34a637db6c0a9b476bbaed5ee/bft/monad-eth-block-policy/src/lib.rs#L77)

Block policy implements static tracking of account balances and nonce updates to allow consensus to lead execution by `k` blocks, by allowing *only valid* transactions to be included in a block.

How it does it is by tracking the “worst case balance” and “nonce” of each account sending transactions and signing EIP-7702 authorizations.

In the case of the “worst case balance” calculation, there is a miscalculation in the `compute_txn_max_gas_cost` function, where the `base_fee` ceiling is applied to transactions that are not EIP-1559 (aka legacy transactions):

```rust
File: bft/monad-eth-block-policy/src/lib.rs
77: pub fn compute_txn_max_gas_cost(txn: &TxEnvelope, base_fee: u64) -> U256 {
78:     let gas_limit = U256::from(txn.gas_limit());
79:     let max_fee = U256::from(txn.max_fee_per_gas());
80:     let priority_fee = U256::from(txn.max_priority_fee_per_gas().unwrap_or(0));
81:     let base_fee = U256::from(base_fee);
82:     let gas_bid = max_fee.min(base_fee.saturating_add(priority_fee));
83:     gas_limit.checked_mul(gas_bid).expect("no overflow")
84: }
```

This contrasts with the execution layer which instead excludes legacy transactions from the EIP-1559 gas ceiling:

```c++
File: bft/monad-cxx/monad-execution/category/execution/ethereum/transaction_gas.cpp
144: inline constexpr uint256_t priority_fee_per_gas(
145:     Transaction const &tx, uint256_t const &base_fee_per_gas) noexcept
146: {
147:     MONAD_ASSERT(tx.max_fee_per_gas >= base_fee_per_gas);
148:     auto const max_priority_fee_per_gas = tx.max_fee_per_gas - base_fee_per_gas;
149: 
150:     if (tx.type == TransactionType::eip1559 ||
151:         tx.type == TransactionType::eip4844 ||
152:         tx.type == TransactionType::eip7702) {
153:         return std::min(tx.max_priority_fee_per_gas, max_priority_fee_per_gas);
154:     }
155:     // EIP-1559: "Legacy Ethereum transactions will still work and
156:     // be included in blocks, but they will not benefit directly from
157:     // the new pricing system. This is due to the fact that upgrading
158:     // from legacy transactions to new transactions results in the
159:     // legacy transaction’s gas_price entirely being consumed either
160:     // by the base_fee_per_gas and the priority_fee_per_gas."
161:     return max_priority_fee_per_gas;
162: }
```

As a result of the bug in the consensus logic, the gas cost of a transaction can be underestimated, allowing transactions to be included in a block when the sender’s balance is not sufficient to guarantee cover for the gas fees.

When these transactions reach execution, the C++ logic will mark them invalid, eventually invalidating the whole block (because transactions that revert are acceptable in a valid block but invalid transactions aren’t).

Apart from the DoS scenario of invalid transactions poisoning blocks, this vulnerability also opens up a scenario where malicious actors can have consensus and include an arbitrarily high number of transactions without paying any fees, thus circumventing the economic barrier of gas that protects the Monad nodes’ infrastructure from abuse.

### Recommended mitigation steps

Fix block policy to calculate legacy transaction gas cost as `gas_limit * gas_price` like done in execution.

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-81)

---
