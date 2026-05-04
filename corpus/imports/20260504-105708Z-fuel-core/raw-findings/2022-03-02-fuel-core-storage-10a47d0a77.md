---
case_id: case_20220302_10a47d0a77
project: fuel-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2022-03-02
source_refs:
  - git:10a47d0a7766eaf43c3a065cd3e4a96c4d8e6d49
  - "fuel-core/src/executor.rs:545"
  - "fuel-core/src/executor.rs:43"
  - "fuel-core/src/executor.rs:188"
  - "fuel-core/src/executor.rs:106"
bug_class: block-malleability
impact_type:
  - integrity
confidence: medium
tags:
  - infrastructure
  - consensus
  - block-malleability
  - block-commitment
  - transaction-serialization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely block-malleability security fix in `fuel-core/src/executor.rs`. The patch changes execution so transaction success statuses are queued with placeholder block ids and persisted only after the finalized block id is known, and it changes the commitment path to include canonical serialization of the malleated transaction including witness data.

## Observed Patch Facts

1. In `fuel-core/src/executor.rs`, the patch adds `fn persist_transaction_status(`.

2. In `fuel-core/src/executor.rs`, the patch replaces `pub async fn execute(` with `pub async fn execute(&self, block: &mut FuelBlock, mode: ExecutionMode) -> Result<(),...`.

3. In `fuel-core/src/executor.rs`, the patch replaces `block_id,` with `block_id: Default::default(),`.

4. In `fuel-core/src/executor.rs`, the patch replaces `// TODO: use SMT instead of this manual approach` with `coinbase = coinbase.checked_add(tx_fee).ok_or(Error::FeeOverflow)?;`.

## Project Context

The changed code sits primarily in `fuel-core/src`, which anchors the finding in the `storage` area of the project. Historical context from `fuel-core/src/tx_pool.rs`, `fuel-core/src/service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `fuel-core/src/tx_pool.rs`, `fuel-core/src/service.rs`. The strongest project-level identifiers around this patch are `block`, `Default::default`, `commitment`, and `TransactionStatus::Success`.

## Before/After Behavior

Before the patch, `Executor::execute` computed a block id at the start, used that value in `TransactionStatus::Success`, persisted status during execution, and updated a rolling commitment from the previous root plus `tx_id` while also accumulating fees in the commitment. After the patch, production execution avoids treating a pre-execution block id as final, successful statuses are created with a placeholder block id, statuses are persisted after being rewritten with the finalized block id, and the commitment path explicitly includes canonical serialized malleated transaction data including witness data while tracking fees separately through `coinbase`.

# Root Cause

The prior execution path appears to have tied status persistence and block commitment to values available before finalization, and the old commitment evidence shows hashing transaction ids rather than canonical serialized executed transaction contents. The provided evidence supports block malleability as the issue, but does not establish a concrete exploit path or impact beyond the protocol identity/commitment invariant.

## Walkthrough

1. Execution enters `Executor::execute`, where the old code computed `let block_id = block.id()` immediately.

2. Successful transaction statuses previously used that early `block_id`.

3. The old commitment update hashed the previous commitment root with `tx_id` and accumulated fees in `commitment.sum`.

4. The patch makes production use a default pre-execution id while validation still computes `block.id()`.

5. Successful statuses are now created with `block_id: Default::default()` and queued in `tx_status`.

6. `persist_transaction_status` later replaces success-status block ids with the finalized block id and persists them.

7. The commitment path now explicitly includes canonical serialization of the malleated transaction, including witness data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| fuel-core/src/executor.rs | 43 | execution entry point computes pre-execution block id differently for production versus validation |
| fuel-core/src/executor.rs | 100 | block commitment construction now includes canonical serialized malleated transaction data and separates fee accumulation into coinbase |
| fuel-core/src/executor.rs | 188 | transaction success status initially uses a placeholder block id while execution continues |
| fuel-core/src/executor.rs | 545 | transaction statuses are persisted after replacing placeholder ids with the finalized block id |

## Code Snippets

## Snippet 1

Context: `fuel-core/src/executor.rs:545` (changes a consensus- or validator-sensitive branch)

Before
```rust
Ok(())
    }
}
```
After
```rust
Ok(())
    }

    fn persist_transaction_status(
        &self,
        finalized_block_id: Bytes32,
        tx_status: &mut [(Bytes32, TransactionStatus)],
        db: &Database,
```

## Snippet 2

Context: `fuel-core/src/executor.rs:43` (changes persisted or aggregate state handling)

Before
```rust
impl Executor {
    pub async fn execute(
        &self,
        block: &mut FuelBlockFull,
        mode: ExecutionMode,
    ) -> Result<(), Error> {
        let block_id = block.id();
```
After
```rust
impl Executor {
    pub async fn execute(&self, block: &mut FuelBlock, mode: ExecutionMode) -> Result<(), Error> {
        // Compute the block id before execution, if mode is set to production just use zeroed id.
        let pre_exec_block_id = match mode {
            ExecutionMode::Production => Default::default(),
            ExecutionMode::Validation => block.id(),
        };
```

## Snippet 3

Context: `fuel-core/src/executor.rs:188` (changes a consensus- or validator-sensitive branch)

Before
```rust
// else tx was a success
                TransactionStatus::Success {
                    block_id,
                    time: block.headers.time,
                    result: *vm_result.state(),
                }
            };
```
After
```rust
// else tx was a success
                TransactionStatus::Success {
                    block_id: Default::default(),
                    time: block.header.time,
                    result: *vm_result.state(),
                }
            };
```

## Snippet 4

Context: `fuel-core/src/executor.rs:106` (changes signature or replay validation logic)

Before
```rust
// update block commitment
            let tx_fee = self.total_fee_paid(tx, vm_result.receipts())?;
            // TODO: use SMT instead of this manual approach
            commitment.sum = commitment
                .sum
                .checked_add(tx_fee)
                .ok_or(Error::FeeOverflow)?;
            commitment.root = Hasher::hash(
```
After
```rust
// update block commitment
            let tx_fee = self.total_fee_paid(tx, vm_result.receipts())?;
            coinbase = coinbase.checked_add(tx_fee).ok_or(Error::FeeOverflow)?;

            // include the canonical serialization of the malleated tx into the commitment,
            // including all witness data.
            //
            // TODO: reference the bytes directly from VM memory to save serialization. This isn't
```

# Fix Pattern

Delay persistence of final block-id-bearing transaction status until finalization, and build block commitments from canonical executed transaction serialization rather than only transaction ids.

## How It Was Fixed

The patch adds `persist_transaction_status`, queues transaction statuses during execution, rewrites successful statuses with the finalized block id before database persistence, separates fee accumulation into `coinbase`, and updates the commitment logic to include canonical serialized malleated transaction data including witnesses.

# Why It Matters

1. Keeps stored transaction status aligned with the finalized block id.

2. Binds block commitment behavior to canonical executed transaction bytes.

3. Addresses a block malleability risk in execution/commitment handling.

4. Does not prove remote exploitability, fund theft, or a permanent consensus split.

# Evidence Notes

Supported by `fuel-core/src/executor.rs` evidence around `Executor::execute`, `TransactionStatus::Success`, `persist_transaction_status`, and the commitment comment stating canonical serialization of the malleated transaction including witness data. The heuristic baseline's panic/liveness narrative is unsupported and removed. The evidence is security-relevant but incomplete, so confidence is medium and verdict is likely rather than confirmed. Protocol security invariant: Block execution should derive finalized block identity and commitments from the canonical executed transaction contents, including witness data, and persisted transaction statuses should reference the finalized block id rather than a pre-finalization placeholder or stale id. Verification notes: The patch does not prove remote exploitability or a demonstrated network attack. The patch does not show a panic-on-malformed-input fix despite the heuristic baseline suggesting one. The patch does not prove funds can be stolen or consensus can be permanently split. The patch evidence is centered on block commitment and status persistence, not mempool admission policy. No evidence supports a panic-on-malformed-input bug class. No evidence supports mempool admission as the affected subsystem. No evidence demonstrates practical exploitability or fund loss. Commit title and code comments support block malleability as the corrected issue. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `block-malleability`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `infrastructure, consensus, block-malleability, block-commitment, transaction-serialization`

The supplied evidence supports retaining this as security hardening rather than a proven security fix. The commit title and executor changes point to block malleability mitigation: production avoids relying on a pre-finalization block id, transaction statuses are rewritten with the finalized block id before persistence, and block commitments are changed to include canonical serialized malleated transaction data including witnesses. However, the patch evidence does not prove an exploitable vulnerability, fund loss, liveness failure, or concrete consensus split.

## Security Evidence

1. Commit subject is explicitly "Malleable Blocks Part 2".
2. Executor now distinguishes production from validation when computing pre-execution block ids.
3. Successful transaction statuses are queued with placeholder block ids and persisted only after being updated to the finalized block id.
4. Commitment logic now includes canonical serialization of the malleated transaction including witness data.
5. The changed code is in block execution, status persistence, and commitment construction paths.

## Missing Evidence

1. No demonstrated attack path or exploit scenario is provided.
2. No evidence shows fund theft, unauthorized state transition, or permanent consensus failure.
3. No evidence supports the original liveness-failure classification.
4. No regression test excerpt directly demonstrates the security invariant or failure mode.

## Claim Boundaries

1. Supported claim: the patch tightens block identity and commitment handling against malleability risk.
2. Supported claim: persisted transaction statuses are made consistent with finalized block ids.
3. Unsupported claim: this is proven exploitable from the patch alone.
4. Unsupported claim: the primary impact is liveness rather than integrity/protocol correctness.
