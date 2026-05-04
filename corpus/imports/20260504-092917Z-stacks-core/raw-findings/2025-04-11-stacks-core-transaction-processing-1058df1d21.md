---
case_id: case_20250411_1058df1d21
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-04-11
source_refs:
  - git:1058df1d21d2c7175301427ae3670c97dcb95105
  - "stackslib/src/net/api/postblock_proposal.rs:594"
  - "stackslib/src/net/api/postblock_proposal.rs:581"
  - "stackslib/src/net/api/postblock_proposal.rs:51"
  - "stackslib/src/net/api/postblock_proposal.rs:622"
bug_class: resource-limit-validation-inconsistency
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - block-proposal-validation
  - replay-validation
  - resource-limits
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit 1058df1d21 changes block proposal replay validation so ChainError::BlockCostExceeded is inspected not only for TransactionResult::ProcessingError, but also for TransactionResult::Skipped and TransactionResult::Problematic. The evidence supports a likely validation bypass in a replay-sensitive resource-control path, but does not prove exploitability, consensus impact, or a broader transaction-processing flaw.

## Observed Patch Facts

1. In `stackslib/src/net/api/postblock_proposal.rs`, the patch replaces `TransactionResult::ProcessingError(e) => {` with `TransactionResult::Skipped(TransactionSkipped { error, .. })`.

2. In `stackslib/src/net/api/postblock_proposal.rs`, the patch adds `// The included tx doesn't match the next tx in the`.

3. In `stackslib/src/net/api/postblock_proposal.rs`, the patch replaces `BlockBuilder, BlockLimitFunction, TransactionError, TransactionResult,` with `BlockBuilder, BlockLimitFunction, TransactionError, TransactionProblematic, Transacti...`.

4. In `stackslib/src/net/api/postblock_proposal.rs`, the patch adds `// TODO: handle other ChainError cases`.

## Project Context

The changed code sits primarily in `stackslib/src/net/api`, `stackslib/src/net`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `stackslib/src/net/api/posttransaction.rs`, `stackslib/src/net/api/poststackerdbchunk.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stackslib/src/net/api/posttransaction.rs`, `stackslib/src/net/api/poststackerdbchunk.rs`. The strongest project-level identifiers around this patch are `TransactionResult::ProcessingError`, `TransactionResult`, `error`, and `TransactionError`. Nearby tests or test-like files include `stackslib/src/net/tests/relay/nakamoto.rs`, `stackslib/src/net/tests/relay/epoch2x.rs`.

## Before/After Behavior

Before the patch, the shown validation branch inspected ChainError::BlockCostExceeded only when try_mine_tx_with_len returned TransactionResult::ProcessingError. After the patch, Skipped, ProcessingError, and Problematic variants are destructured into a shared error path, so BlockCostExceeded leads to the same InvalidTransactionReplay rejection across those variants. Other ChainError cases remain allowed to be dropped via continue.

# Root Cause

The validation logic was tied to a specific TransactionResult variant instead of consistently enforcing the BlockCostExceeded rejection on the underlying error. If try_mine_tx_with_len reported the same block-cost failure through Skipped or Problematic, the provided diff indicates the old code would not apply the evidenced InvalidTransactionReplay handling in that branch.

## Walkthrough

1. During Nakamoto block proposal validation, the code compares an included transaction with the next transaction expected from the replay set.

2. When the transaction IDs differ, validation calls builder.try_mine_tx_with_len on the replay transaction to decide whether it can be skipped as unmineable.

3. The before snippet shows ChainError::BlockCostExceeded handling only under TransactionResult::ProcessingError.

4. The patch imports TransactionSkipped and TransactionProblematic and adds them to the same match arm as TransactionError.

5. All three variants now expose their underlying error to the same ChainError match.

6. If that error is BlockCostExceeded, validation returns InvalidTransactionReplay.

7. The result is variant-independent handling for the evidenced block-cost rejection case.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stackslib/src/net/api/postblock_proposal.rs | 581 | Detects a proposed transaction that does not match the next transaction in the replay set and probes whether the replay transaction can be skipped as unmineable. |
| stackslib/src/net/api/postblock_proposal.rs | 594 | Normalizes Skipped, ProcessingError, and Problematic transaction mining results to inspect their underlying ChainError. |
| stackslib/src/net/api/postblock_proposal.rs | 616 | Rejects validation with InvalidTransactionReplay when the underlying transaction failure is ChainError::BlockCostExceeded. |
| stackslib/src/net/api/postblock_proposal.rs | 51 | Imports TransactionSkipped and TransactionProblematic so validation can handle all relevant failure result variants. |

## Code Snippets

## Snippet 1

Context: `stackslib/src/net/api/postblock_proposal.rs:594` (changes signature or replay validation logic)

Before
```rust
);
                    match tx_result {
                        TransactionResult::ProcessingError(e) => {
                            // The tx wasn't able to be mined. Check `TransactionError`, to
                            // see if we should error or allow the tx to be dropped from the replay set.

                            // TODO: handle TransactionError cases
                            match e.error {
```
After
```rust
);
                    match tx_result {
                        TransactionResult::Skipped(TransactionSkipped { error, .. })
                        | TransactionResult::ProcessingError(TransactionError { error, .. })
                        | TransactionResult::Problematic(TransactionProblematic {
                            error, ..
                        }) => {
                            // The tx wasn't able to be mined. Check the underlying error, to
```

## Snippet 2

Context: `stackslib/src/net/api/postblock_proposal.rs:581` (changes a sensitive control or state-update path)

Before
```rust
break;
                    }
                    let tx_result = builder.try_mine_tx_with_len(
                        &mut tenure_tx,
```
After
```rust
break;
                    }

                    // The included tx doesn't match the next tx in the
                    // replay set. Check to see if the tx is skipped because
                    // it was unmineable.
                    let tx_result = builder.try_mine_tx_with_len(
                        &mut tenure_tx,
```

## Snippet 3

Context: `stackslib/src/net/api/postblock_proposal.rs:51` (changes a sensitive control or state-update path)

Before
```rust
use crate::chainstate::stacks::db::{StacksBlockHeaderTypes, StacksChainState};
use crate::chainstate::stacks::miner::{
    BlockBuilder, BlockLimitFunction, TransactionError, TransactionResult,
};
use crate::chainstate::stacks::{
```
After
```rust
use crate::chainstate::stacks::db::{StacksBlockHeaderTypes, StacksChainState};
use crate::chainstate::stacks::miner::{
    BlockBuilder, BlockLimitFunction, TransactionError, TransactionProblematic, TransactionResult,
    TransactionSkipped,
};
use crate::chainstate::stacks::{
```

## Snippet 4

Context: `stackslib/src/net/api/postblock_proposal.rs:622` (changes a sensitive control or state-update path)

Before
```rust
});
                                }
                                _ => {
                                    // it's ok, drop it
```
After
```rust
});
                                }
                                // TODO: handle other ChainError cases
                                _ => {
                                    // it's ok, drop it
```

# Fix Pattern

Normalize equivalent transaction failure variants before applying resource-limit validation decisions.

## How It Was Fixed

The match on tx_result in stackslib/src/net/api/postblock_proposal.rs was broadened from ProcessingError-only handling to a combined arm for Skipped, ProcessingError, and Problematic. Each variant now binds its underlying error and passes it through the existing ChainError::BlockCostExceeded rejection logic.

# Why It Matters

1. Replay-set validation affects whether a block proposal can omit or reorder expected transactions.

2. BlockCostExceeded is treated by this code as a reason to reject, not silently drop, the replay transaction.

3. The prior behavior could depend on the outer TransactionResult variant rather than the underlying failure reason.

4. The evidence does not establish a crash, cryptographic break, or proven remote exploit.

# Evidence Notes

Grounded evidence is limited to stackslib/src/net/api/postblock_proposal.rs lines around imports, replay mismatch handling, the broadened TransactionResult match, and the BlockCostExceeded rejection. The test files were touched but their contents are not provided. Claims about panic-prone conversions, malformed decoding, signatures, or remote denial of service are unsupported by the supplied snippets and have been removed. Protocol security invariant: A Nakamoto block proposal validator should apply replay-set and block-cost rejection rules based on the underlying transaction failure reason, not on which TransactionResult wrapper carries that error. A replay transaction that fails with ChainError::BlockCostExceeded should not be treated as safely droppable during proposal validation. Verification notes: The patch does not prove remote exploitability or a concrete attack flow by itself. The evidence does not show a crash, panic, signature bypass, or cryptographic break. The exact consensus impact is not fully proven from the provided snippets alone. Only BlockCostExceeded handling in block proposal replay validation is evidenced, not a broader transaction validation flaw. Confirmed by diff evidence: ProcessingError-only handling became shared handling for Skipped, ProcessingError, and Problematic. Confirmed by diff evidence: ChainError::BlockCostExceeded maps to ValidateRejectCode::InvalidTransactionReplay in the shown path. Not proven by provided evidence: remote exploitability or exact consensus impact. Not proven by provided evidence: crash, panic, serialization, or cryptographic failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-limit-validation-inconsistency`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, block-proposal-validation, replay-validation, resource-limits, consensus`

The supplied patch evidence supports retaining this as security hardening, not a proven security fix. The change broadens block proposal replay validation so BlockCostExceeded is handled consistently across Skipped, ProcessingError, and Problematic transaction results, causing an InvalidTransactionReplay rejection instead of allowing the transaction to be dropped. That is a security-sensitive validation and resource-control path in blockchain consensus logic, but the snippets do not prove exploitability, a concrete consensus split, signature impact, or liveness failure.

## Security Evidence

1. Block proposal validation inspects replay-set mismatch handling in stackslib/src/net/api/postblock_proposal.rs.
2. The before code handled ChainError::BlockCostExceeded only for TransactionResult::ProcessingError.
3. The after code also handles TransactionResult::Skipped and TransactionResult::Problematic by extracting the same underlying error.
4. When the underlying error is BlockCostExceeded, the path returns ValidateRejectCode::InvalidTransactionReplay.
5. The change is in a resource-limit and replay-validation path, which is security-sensitive in blockchain core code.

## Missing Evidence

1. No supplied test contents showing the exact regression or attack scenario.
2. No proof that an external attacker could trigger the affected variants in a harmful block proposal.
3. No demonstrated consensus split, chain acceptance divergence, crash, or denial-of-service impact.
4. No evidence supporting signature-related tags or cryptographic failure claims.
5. No full surrounding match behavior proving every pre-patch outcome outside the shown snippets.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix because exploitability is not established.
2. Limit the bug class to inconsistent BlockCostExceeded handling across TransactionResult variants.
3. Do not claim a signature bypass, cryptographic break, panic, serialization flaw, or remote exploit.
4. Do not claim a confirmed liveness failure from the supplied patch alone.
5. Consensus-integrity relevance is inferred from block proposal replay validation, not proven by an end-to-end failure trace.
