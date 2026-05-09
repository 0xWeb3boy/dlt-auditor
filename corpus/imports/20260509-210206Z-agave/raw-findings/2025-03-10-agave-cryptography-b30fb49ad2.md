---
case_id: case_20250310_b30fb49ad2
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2025-03-10
source_refs:
  - git:b30fb49ad2e465ed18b55fdb5b3cb5c820b5cf2d
  - "core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:678"
  - "core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:786"
  - "core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:431"
  - "core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:445"
bug_class: panic-on-invalid-transaction
impact_type:
  - availability
confidence: medium
tags:
  - blockchain-core
  - banking-stage
  - transaction-buffering
  - expired-blockhash
  - panic
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a TransactionView receive-and-buffer panic by adding `continue;` after removing errored transactions from the container. Without that control-flow break, the same loop iteration could attempt to fetch the removed transaction id through an `expect("transaction must exist")` path.

## Observed Patch Facts

1. In `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs`, the patch replaces `#[test]` with `super::*,`.

2. In `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs`, the patch adds `#[test_case(setup_sanitized_transaction_receive_and_buffer; "testcase-sdk")]`.

3. In `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs`, the patch adds `continue;`.

4. In `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs`, the patch adds `continue;`.

## Project Context

The changed code sits primarily in `core/src/banking_stage/transaction_scheduler`, `core/src/banking_stage`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/banking_stage/transaction_scheduler/transaction_state_container.rs`, `core/src/banking_stage/transaction_scheduler/scheduler_controller.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/banking_stage/transaction_scheduler/transaction_state_container.rs`, `core/src/banking_stage/transaction_scheduler/scheduler_controller.rs`. The strongest project-level identifiers around this patch are `container`, `crate::banking_stage::tests::create_slow_genesis_config`, `solana_ledger::genesis_utils::GenesisConfigInfo`, and `solana_perf::packet`.

## Before/After Behavior

Before the patch, two error branches removed `priority_id.id` from the TransactionView container but then allowed execution to continue. The surrounding code shows a later lookup of the same id using `container.get_transaction_ttl(priority_id.id).expect("transaction must exist")`, so a transaction rejected for status, age, expired blockhash, or fee-payer validation could trigger a panic after removal. After the patch, both branches skip the rest of the iteration immediately after removal.

# Root Cause

The TransactionView buffering loop had inconsistent control flow after deleting invalid transactions. It removed entries from the container but still executed later code that assumed those entries existed.

## Walkthrough

1. The TransactionView receive path builds transaction ids that refer to entries in a scheduler container.

2. The code runs bank transaction checks using `MAX_PROCESSING_AGE`.

3. If a check result is an error, the transaction id is removed from the container.

4. Before the fix, execution could continue after removal.

5. The next visible path re-fetches the same id with `expect("transaction must exist")`.

6. For a removed id, that lookup could panic instead of treating the transaction as dropped invalid input.

7. A similar fallthrough existed after `Consumer::check_fee_payer_unlocked` returned an error.

8. The patch adds `continue;` after each removal, preventing later dereference of the deleted id.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs | 372 | TransactionView packet batch receive path builds buffered transaction ids and runs age/status checks before queueing. |
| core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs | 431 | After `check_transactions` reports an error, the transaction is removed from the container and now skipped to avoid later lookup of a deleted id. |
| core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs | 445 | After fee-payer/status validation fails, the transaction is removed from the container and now skipped to avoid later lookup of a deleted id. |
| core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs | 786 | Regression coverage exercises receive-and-buffer behavior for both sanitized transaction and transaction view implementations. |

## Code Snippets

## Snippet 1

Context: `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:678` (changes signature or replay validation logic)

Before
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
```
After
```rust
#[cfg(test)]
mod tests {
    use {
        super::*,
        crate::banking_stage::tests::create_slow_genesis_config,
        crossbeam_channel::{unbounded, Receiver},
        solana_ledger::genesis_utils::GenesisConfigInfo,
        solana_perf::packet::{to_packet_batches, Packet, PacketBatch},
```

## Snippet 2

Context: `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:786` (changes signature or replay validation logic)

Before
```rust
);
    }
}
```
After
```rust
);
    }

    #[test_case(setup_sanitized_transaction_receive_and_buffer; "testcase-sdk")]
    #[test_case(setup_transaction_view_receive_and_buffer; "testcase-view")]
    fn test_receive_and_buffer_disconnected_channel<R: ReceiveAndBuffer>(
        setup_receive_and_buffer: impl FnOnce(
            Receiver<BankingPacketBatch>,
```

## Snippet 3

Context: `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:431` (changes a sensitive control or state-update path)

Before
```rust
num_dropped_on_status_age_checks += 1;
                        container.remove_by_id(priority_id.id);
                    }
                    let transaction = &container
```
After
```rust
num_dropped_on_status_age_checks += 1;
                        container.remove_by_id(priority_id.id);
                        continue;
                    }
                    let transaction = &container
```

## Snippet 4

Context: `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs:445` (changes a sensitive control or state-update path)

Before
```rust
num_dropped_on_status_age_checks += 1;
                        container.remove_by_id(priority_id.id);
                    }
                }
```
After
```rust
num_dropped_on_status_age_checks += 1;
                        container.remove_by_id(priority_id.id);
                        continue;
                    }
                }
```

# Fix Pattern

After removing the current invalid item from an indexed container, immediately stop processing that item before any later code can dereference its removed id.

## How It Was Fixed

The patch adds `continue;` after `container.remove_by_id(priority_id.id)` in both affected TransactionView error branches: one after `check_transactions` reports an error and one after `check_fee_payer_unlocked` fails. Test coverage was also expanded around receive-and-buffer behavior.

# Why It Matters

1. Invalid or expired transactions should be dropped without panicking the node process.

2. The affected path is part of BankingStage packet receive and buffering.

3. The supported impact is availability, not signature bypass or consensus violation.

4. The evidence supports the TransactionView path specifically.

# Evidence Notes

The strongest evidence is the focused runtime diff in `core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs`: two added `continue;` statements immediately after `container.remove_by_id(priority_id.id)`. The surrounding excerpt shows a later `get_transaction_ttl(...).expect("transaction must exist")`, grounding the panic-after-removal claim. The commit subject names expired blockhashes for the view path. The provided evidence does not establish a cryptographic bypass, consensus safety issue, or the same panic in the sanitized transaction path. Protocol security invariant: The packet receive-and-buffer path must drop transactions that fail age, status, or fee-payer checks without continuing to use transaction ids that were removed from the scheduler container. Verification notes: The patch does not prove a consensus safety violation. The patch does not show signature or cryptographic verification bypass. Remote exploitability is plausible from the packet receive path but not fully demonstrated by the provided evidence. The concrete fixed failure is a panic in the TransactionView buffering path after expired blockhash/status-age rejection. No evidence is provided that the sanitized transaction path had the same panic. No command output or full test result was provided. Remote exploitability is not fully demonstrated, but the packet receive path and expired-transaction trigger make availability impact likely. Helper test imports and test cases should be treated as regression support, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `panic-on-invalid-transaction`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `blockchain-core, banking-stage, transaction-buffering, expired-blockhash, panic, availability`

The patch evidence supports a focused fix for a panic in the TransactionView receive-and-buffer path: invalid or expired transactions were removed from the container but processing could continue to code that expected the transaction id to still exist. Because this is in a packet receive/buffering path and the commit subject names expired blockhashes, it is plausibly security-relevant as availability hardening. The evidence does not confidently prove a concrete exploitable security bug, cryptographic issue, signature bypass, or consensus failure, so security-hardening is more appropriate than security-fix.

## Security Evidence

1. Two runtime branches add continue immediately after container.remove_by_id(priority_id.id).
2. The surrounding context shows later lookups using expect("transaction must exist") on the same transaction id.
3. The commit subject explicitly says it fixes a panic on expired blockhashes for the view path.
4. The affected code is in BankingStage transaction receive and buffering, which handles transaction packet flow.

## Missing Evidence

1. No proof is provided that the panic terminates the whole validator process or causes network-wide denial of service.
2. No exploit path or externally submitted transaction reproduction is shown beyond the expired blockhash implication.
3. No evidence supports cryptographic bypass, signature validation failure, or consensus safety impact.
4. Test evidence is mostly regression coverage and does not by itself establish exploitability.

## Claim Boundaries

1. Validated only for the TransactionView receive-and-buffer path shown in the evidence.
2. Supported impact is availability hardening against panic, not integrity or cryptographic compromise.
3. Do not classify this as a signature, replay, or consensus bug from the supplied patch alone.
4. The sanitized transaction path is not proven to have had the same panic.
