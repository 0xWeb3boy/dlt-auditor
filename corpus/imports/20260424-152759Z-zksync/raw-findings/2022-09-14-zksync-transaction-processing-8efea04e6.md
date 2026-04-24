---
case_id: case_20220914_8efea04e6
project: zksync
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2022-09-14
source_refs:
  - git:8efea04e6c72023c35bf35f24a4bd0ed6bfff701
  - "core/lib/storage/src/withdrawals/mod.rs:47"
  - "core/lib/types/src/withdrawals.rs:83"
  - "core/lib/types/src/withdrawals.rs:106"
  - "core/lib/types/src/withdrawals.rs:119"
bug_class: withdrawal-finalization-ordering
impact_type:
  - state-integrity
  - fund-availability
tags:
  - withdrawals
  - transaction-processing
  - event-ordering
  - idempotency
  - parser-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a likely withdrawal finalization correctness/security fix. The patch changes the duplicate-processing guard from a coarse maximum processed block check to a per-block maximum log-index check, and adds `log_index` to `WithdrawalEvent` so multiple withdrawal logs in the same block can be distinguished. The parser assertion changes are grounded robustness improvements but are not independently proven to be exploitable security fixes.

## Observed Patch Facts

1. In `core/lib/storage/src/withdrawals/mod.rs`, the patch replaces `let max_processed_block =` with `let max_processed_log = sqlx::query_scalar!(`.

2. In `core/lib/types/src/withdrawals.rs`, the patch replaces `if event.topics.len() != 3 {` with `if event.topics.len() != 3 || event.data.0.len() != 32 * 2 {`.

3. In `core/lib/types/src/withdrawals.rs`, the patch replaces `if event.topics.len() != 3 {` with `if event.topics.len() != 3 || event.data.0.len() != 32 {`.

4. In `core/lib/types/src/withdrawals.rs`, the patch adds `log_index: event.log_index.unwrap().as_u64(),`.

## Project Context

The changed code sits primarily in `core/lib/storage/src/withdrawals`, `core/lib/storage/src`, `core/lib/types/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/lib/types/src/tokens.rs`, `core/lib/types/src/register_factory.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/lib/types/src/tokens.rs`, `core/lib/types/src/register_factory.rs`. The strongest project-level identifiers around this patch are `event`, `U256::from_big_endian`, `data`, and `sqlx::query_scalar`. Nearby tests or test-like files include `core/lib/storage/src/tests/event.rs`, `core/lib/storage/src/tests/data_restore.rs`.

## Before/After Behavior

Before the patch, `finalize_withdrawal` queried the maximum processed withdrawal block across all withdrawals and returned early when that block was greater than or equal to the incoming event block, so another withdrawal log in the same block could be skipped as already processed. After the patch, it queries the maximum processed log index for the incoming block and compares it with the incoming event `log_index`. Before the patch, withdrawal event parsers checked only topic count before asserting expected data length. After the patch, they return parse errors when data length is not the expected 32 or 64 bytes.

# Root Cause

The finalization idempotency marker used only block number, which is too coarse for Ethereum logs because a single block can contain multiple withdrawal events. The data-length assertion issue is a separate robustness weakness: malformed payload shape was not handled through the normal parse-error path.

## Walkthrough

1. `WithdrawalEvent` is built from an Ethereum log in `core/lib/types/src/withdrawals.rs`.

2. Before the change, the parsed event did not carry `event.log_index`.

3. `finalize_withdrawal` in `core/lib/storage/src/withdrawals/mod.rs` checked only `MAX(withdrawal_tx_block)` across withdrawals.

4. If any withdrawal from block N had been processed, another withdrawal from the same block N could satisfy the old early-return condition.

5. The patch records `event.log_index.unwrap().as_u64()` in `WithdrawalEvent`.

6. The finalization query now selects `MAX(withdrawal_tx_log_index)` scoped to the incoming `withdrawal_tx_block`.

7. The early-return check now operates on log ordering within the same block instead of treating the whole block as processed.

8. The parser changes replace data-length assertions with explicit parse-error returns for unexpected withdrawal log payload sizes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/lib/storage/src/withdrawals/mod.rs | 47 | finalizes withdrawal events and enforces duplicate-processing guard using block number plus log index |
| core/lib/types/src/withdrawals.rs | 83 | parses pending withdrawal logs and validates expected topic/data shape before decoding |
| core/lib/types/src/withdrawals.rs | 106 | parses finalized withdrawal logs and validates expected topic/data shape before decoding |
| core/lib/types/src/withdrawals.rs | 119 | carries Ethereum log_index into WithdrawalEvent so storage can distinguish multiple logs in one block |

## Code Snippets

## Snippet 1

Context: `core/lib/storage/src/withdrawals/mod.rs:47` (changes a sensitive control or state-update path)

Before
```rust
pub async fn finalize_withdrawal(&mut self, withdrawal: &WithdrawalEvent) -> QueryResult<()> {
        let mut transaction = self.0.start_transaction().await?;
        let max_processed_block =
            sqlx::query_scalar!("SELECT MAX(withdrawal_tx_block) FROM withdrawals")
                .fetch_one(transaction.conn())
                .await?;
        // We have already processed txs from this block
        if let Some(block) = max_processed_block {
```
After
```rust
pub async fn finalize_withdrawal(&mut self, withdrawal: &WithdrawalEvent) -> QueryResult<()> {
        let mut transaction = self.0.start_transaction().await?;
        let max_processed_log = sqlx::query_scalar!(
            "SELECT MAX(withdrawal_tx_log_index) FROM withdrawals WHERE withdrawal_tx_block= $1",
            withdrawal.block_number as i64
        )
        .fetch_one(transaction.conn())
        .await?;
```

## Snippet 2

Context: `core/lib/types/src/withdrawals.rs:83` (changes the branch that decides whether execution stops or continues)

Before
```rust
fn try_from(event: Log) -> Result<WithdrawalPendingEvent, WithdrawalPendingParseError> {
        if event.topics.len() != 3 {
            return Err(WithdrawalPendingParseError::ParseError(event));
        }
        assert_eq!(event.data.0.len(), 32 * 2);
        let amount = U256::from_big_endian(&event.data.0[..32]);
        let tx_type = WithdrawalType::try_from(U256::from_big_endian(&event.data.0[32..]))?;
```
After
```rust
fn try_from(event: Log) -> Result<WithdrawalPendingEvent, WithdrawalPendingParseError> {
        if event.topics.len() != 3 || event.data.0.len() != 32 * 2 {
            return Err(WithdrawalPendingParseError::ParseError(event));
        }
        let amount = U256::from_big_endian(&event.data.0[..32]);
        let tx_type = WithdrawalType::try_from(U256::from_big_endian(&event.data.0[32..]))?;
```

## Snippet 3

Context: `core/lib/types/src/withdrawals.rs:106` (changes the branch that decides whether execution stops or continues)

Before
```rust
fn try_from(event: Log) -> Result<WithdrawalEvent, WithdrawalPendingParseError> {
        if event.topics.len() != 3 {
            return Err(WithdrawalPendingParseError::ParseError(event));
        }

        assert_eq!(event.data.0.len(), 32);
        let amount = U256::from_big_endian(&event.data.0);
```
After
```rust
fn try_from(event: Log) -> Result<WithdrawalEvent, WithdrawalPendingParseError> {
        if event.topics.len() != 3 || event.data.0.len() != 32 {
            return Err(WithdrawalPendingParseError::ParseError(event));
        }

        let amount = U256::from_big_endian(&event.data.0);
        Ok(WithdrawalEvent {
```

## Snippet 4

Context: `core/lib/types/src/withdrawals.rs:119` (changes the branch that decides whether execution stops or continues)

Before
```rust
amount,
            tx_hash: event.transaction_hash.unwrap(),
        })
    }
```
After
```rust
amount,
            tx_hash: event.transaction_hash.unwrap(),
            log_index: event.log_index.unwrap().as_u64(),
        })
    }
```

# Fix Pattern

Use the full event ordering key for idempotency: block number plus log index. Validate log payload length before decoding rather than relying on assertions.

## How It Was Fixed

The storage query was changed from a global maximum withdrawal block to the maximum withdrawal log index for the specific block being processed. `WithdrawalEvent` now includes the Ethereum log index needed by that query. The withdrawal log parsers now reject unexpected data lengths through `WithdrawalPendingParseError::ParseError`.

# Why It Matters

1. Multiple withdrawal logs can occur in one L1 block.

2. A block-level deduplication guard can incorrectly skip distinct withdrawal events.

3. Skipping withdrawal finalization can plausibly affect user fund availability.

4. The evidence does not support claims of theft, arbitrary withdrawal creation, or consensus compromise.

5. The malformed-log handling change is safer failure handling, but exploitability is not established.

# Evidence Notes

Grounded evidence comes from `core/lib/storage/src/withdrawals/mod.rs` line 47, where the guard changes from `MAX(withdrawal_tx_block)` to `MAX(withdrawal_tx_log_index)` scoped by block, and from `core/lib/types/src/withdrawals.rs` line 119, where `log_index` is added to `WithdrawalEvent`. Parser evidence at lines 83 and 106 supports a robustness change from `assert_eq!` to normal parse errors. Migration and sqlx metadata are support changes, not root-cause evidence. Claims about attacker control, fund theft, arbitrary withdrawals, proof-system compromise, or consensus failure are not supported by the provided input. Protocol security invariant: Withdrawal finalization should distinguish each L1 withdrawal event within a block, using block number plus log index, so that one processed withdrawal log does not cause later withdrawal logs from the same block to be treated as already finalized. Verification notes: The patch does not prove an attacker can mint funds or create arbitrary withdrawals. The patch does not prove malformed logs are attacker-controllable in production. The patch does not prove consensus or proof-system compromise. The observed impact is limited to withdrawal event parsing/finalization behavior shown in the provided hunks. The migration and sqlx baseline updates are supporting changes, not independent security evidence. Code evidence supports the same-block withdrawal skip scenario. Security impact is inferred as withdrawal availability/integrity risk, not directly demonstrated by an exploit or commit message. Parser hardening should be treated as supporting robustness unless additional evidence shows malformed logs are attacker-controllable in production. No external context or file inspection was used. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `withdrawal-finalization-ordering`
Final impact type: `state-integrity, fund-availability`
Final tags: `withdrawals, transaction-processing, event-ordering, idempotency, parser-hardening`

The patch is security-relevant because it fixes withdrawal finalization logic in a financial transaction path: the old guard treated an entire block as processed after seeing any withdrawal in that block, while the new guard distinguishes events by per-block log index. That supports a conservative security-hardening classification, but the evidence does not prove an attacker-controlled exploit or concrete theft/state corruption, so security-fix is too strong.

## Security Evidence

1. Withdrawal finalization changed from global MAX(withdrawal_tx_block) to MAX(withdrawal_tx_log_index) scoped to the incoming block.
2. WithdrawalEvent now carries event.log_index, allowing multiple withdrawal logs in the same block to be distinguished.
3. Old behavior could skip later withdrawal events in a block once any withdrawal from that block had been processed.
4. Withdrawal log parsers now reject malformed data lengths with parse errors instead of assert_eq panics.

## Missing Evidence

1. No commit message or advisory states this was a security vulnerability.
2. No exploit path shows an attacker can trigger same-block withdrawal skipping intentionally.
3. No evidence proves funds can be stolen, arbitrary withdrawals created, or consensus/proof integrity compromised.
4. Malformed log exploitability is not established from the patch alone.

## Claim Boundaries

1. Retain as security-hardening, not a confirmed security-fix.
2. Supported impact is limited to withdrawal finalization correctness and possible fund availability/state integrity risk.
3. Parser assertion changes should be treated as robustness hardening unless attacker-controlled malformed logs are proven.
4. Do not claim theft, minting, arbitrary withdrawal creation, or consensus compromise from this evidence.
