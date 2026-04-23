---
case_id: case_20230926_eb6dc5197
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2023-09-26
source_refs:
  - git:eb6dc51971c90de0dddd3a24a34d968ec9f8cb60
  - "crates/consensus/beacon/src/engine/mod.rs:1144"
  - "crates/consensus/beacon/src/engine/mod.rs:1197"
  - "crates/consensus/beacon/src/engine/mod.rs:1186"
  - "crates/rpc/rpc-types-compat/src/engine/payload.rs:258"
bug_class: consensus-rule-validation
impact_type:
  - consensus-integrity
  - protocol-input-validation
confidence: medium
tags:
  - blockchain-core
  - consensus
  - engine-api
  - payload-validation
  - fork-gating
  - blob-transactions
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit pre-Cancun no-blob check in the beacon engine's payload-validation path and routes that case through a distinct `BeaconOnNewPayloadError`. The evidence supports that a fork-specific validation step was missing in this path, but it does not by itself prove prior acceptance into canonical state, exploitability, or a realized consensus failure.

## Observed Patch Facts

1. In `crates/consensus/beacon/src/engine/mod.rs`, the patch replaces `) -> Result<SealedBlock, PayloadStatus> {` with `/// - the block does not contain blob transactions if it is pre-cancun`.

2. In `crates/consensus/beacon/src/engine/mod.rs`, the patch replaces `self.validate_versioned_hashes(parent_hash, block_versioned_hashes, cancun_fields)?;` with `if let Err(status) =`.

3. In `crates/consensus/beacon/src/engine/mod.rs`, the patch replaces `return Err(PayloadStatus::new(status, latest_valid_hash))` with `return Ok(Err(PayloadStatus::new(status, latest_valid_hash)))`.

4. In `crates/rpc/rpc-types-compat/src/engine/payload.rs`, the patch replaces `/// Tries to create a new block from the given payload and optional parent beacon blo...` with `/// Tries to create a new block (without a block hash) from the given payload and opt...`.

## Project Context

The changed code sits primarily in `crates/consensus/beacon/src/engine`, `crates/consensus/beacon/src`, `crates/rpc/rpc-types-compat/src/engine`, which anchors the finding in the `storage` area of the project. Historical context from `crates/consensus/beacon/src/engine/message.rs`, `crates/consensus/beacon/src/engine/metrics.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/beacon/src/engine/message.rs`, `crates/consensus/beacon/src/engine/test_utils.rs`. The strongest project-level identifiers around this patch are `block`, `payload`, `PayloadStatus::new`, and `status`.

## Before/After Behavior

Before the patch, `ensure_well_formed_payload` returned `Result<SealedBlock, PayloadStatus>`, built a sealed block via `try_into_sealed_block`, and then validated versioned hashes; the provided excerpts do not show an explicit rule rejecting blob transactions before Cancun. After the patch, the function returns `Result<Result<SealedBlock, PayloadStatus>, BeaconOnNewPayloadError>`, uses `try_into_block`, checks `!is_cancun_active_at_timestamp(block.timestamp) && block.has_blob_transactions()` before block-hash validation, and returns `BeaconOnNewPayloadError::PreCancunBlockWithBlobTransactions` for that case while preserving ordinary invalid-payload handling as `Ok(Err(...))`.

# Root Cause

The shown validation entrypoint lacked an explicit fork-gated check for blob transactions on pre-Cancun timestamps, and the old flow constructed or validated a sealed block before exposing a place to apply that rule in this function.

## Walkthrough

1. `ensure_well_formed_payload` gains a documented rule that pre-Cancun blocks must not contain blob transactions.

2. Its return type changes to a nested result, separating `PayloadStatus` outcomes from `BeaconOnNewPayloadError`.

3. The implementation switches from `try_into_sealed_block` to `try_into_block`, allowing inspection of the unsealed block before hash validation.

4. The new code checks whether Cancun is inactive at `block.timestamp` and whether the block contains blob transactions.

5. If both conditions hold, it returns `BeaconOnNewPayloadError::PreCancunBlockWithBlobTransactions`.

6. Other payload-construction, hash-validation, and versioned-hash failures are still converted into `PayloadStatus`, now wrapped as `Ok(Err(...))`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/consensus/beacon/src/engine/mod.rs | 1138 | Primary new-payload consensus validation entrypoint; documents and enforces the added pre-Cancun no-blob invariant. |
| crates/consensus/beacon/src/engine/mod.rs | 1147 | Checks block timestamp against Cancun activation and rejects blob transactions before block-hash validation, changing control flow and error classification. |
| crates/consensus/beacon/src/engine/mod.rs | 1186 | Converts prior direct invalid-payload returns into nested result handling so protocol-invalid cases and engine API errors are separated. |
| crates/consensus/beacon/src/engine/mod.rs | 1197 | Preserves versioned-hash validation under the new result structure after the block has passed fork-specific checks. |
| crates/rpc/rpc-types-compat/src/engine/payload.rs | 250 | Splits payload conversion into an unsealed block construction path, enabling fork-rule checks before sealed-block/hash validation. |

## Code Snippets

## Snippet 1

Context: `crates/consensus/beacon/src/engine/mod.rs:1144` (changes a sensitive control or state-update path)

Before
```rust
///    - the versioned hashes passed with the payload do not exactly match transaction
    ///    versioned hashes
    fn ensure_well_formed_payload(
        &self,
        payload: ExecutionPayload,
        cancun_fields: Option<CancunPayloadFields>,
    ) -> Result<SealedBlock, PayloadStatus> {
        let parent_hash = payload.parent_hash();
```
After
```rust
///    - the versioned hashes passed with the payload do not exactly match transaction
    ///    versioned hashes
    ///    - the block does not contain blob transactions if it is pre-cancun
    fn ensure_well_formed_payload(
        &self,
        payload: ExecutionPayload,
        cancun_fields: Option<CancunPayloadFields>,
    ) -> Result<Result<SealedBlock, PayloadStatus>, BeaconOnNewPayloadError> {
```

## Snippet 2

Context: `crates/consensus/beacon/src/engine/mod.rs:1197` (changes a sensitive control or state-update path)

Before
```rust
.collect::<Vec<_>>();

        self.validate_versioned_hashes(parent_hash, block_versioned_hashes, cancun_fields)?;

        Ok(block)
    }
```
After
```rust
.collect::<Vec<_>>();

        if let Err(status) =
            self.validate_versioned_hashes(parent_hash, block_versioned_hashes, cancun_fields)
        {
            return Ok(Err(status))
        }
```

## Snippet 3

Context: `crates/consensus/beacon/src/engine/mod.rs:1186` (changes a sensitive control or state-update path)

Before
```rust
let status = PayloadStatusEnum::from(error);

                return Err(PayloadStatus::new(status, latest_valid_hash))
            }
        };
```
After
```rust
let status = PayloadStatusEnum::from(error);

                return Ok(Err(PayloadStatus::new(status, latest_valid_hash)))
            }
        };
```

## Snippet 4

Context: `crates/rpc/rpc-types-compat/src/engine/payload.rs:258` (changes a sensitive control or state-update path)

Before
```rust
}

/// Tries to create a new block from the given payload and optional parent beacon block root.
/// Perform additional validation of `extra_data` and `base_fee_per_gas` fields.
///
/// NOTE: The log bloom is assumed to be validated during serialization.
/// NOTE: Empty ommers, nonce and difficulty values are validated upon computing block hash and
/// comparing the value with `payload.block_hash`.
```
After
```rust
}

/// Tries to create a new block (without a block hash) from the given payload and optional parent
/// beacon block root.
/// Performs additional validation of `extra_data` and `base_fee_per_gas` fields.
///
/// NOTE: The log bloom is assumed to be validated during serialization.
///
```

# Fix Pattern

Add explicit fork-aware validation before downstream sealing or hash validation, and use a separate error path for malformed or disallowed inputs when the API requires different handling.

## How It Was Fixed

The fix introduces an unsealed block-construction path (`try_into_block`) and uses it in `ensure_well_formed_payload` so the engine can inspect timestamp and transaction contents before block-hash validation. That enables an explicit rejection when a pre-Cancun payload contains blob transactions, while leaving existing invalid-payload status reporting in place for other failures.

# Why It Matters

1. It makes the pre-Cancun no-blob rule explicit in a consensus-sensitive validation path.

2. It checks the condition before block-hash validation, matching the comment about returning `INVALID_PARAMS` instead of ordinary invalid status.

3. It separates this case from routine `PayloadStatus` failures.

4. The evidence shows missing validation was corrected, but not the full impact of the prior behavior.

# Evidence Notes

The strongest support is in `crates/consensus/beacon/src/engine/mod.rs`, where the doc comment, function signature, and new conditional on `block.timestamp` plus `block.has_blob_transactions()` are all visible. `crates/rpc/rpc-types-compat/src/engine/payload.rs` shows the companion introduction of `try_into_block`, which explains how the new early check became possible. The excerpts support a missing validation/error-classification fix in this code path. They do not, on their own, prove that pre-patch code would accept such payloads into canonical state or that this led to a concrete security exploit. Protocol security invariant: New-payload validation should enforce fork-gated consensus rules before a payload is treated as well formed. In the supplied evidence, that specifically means rejecting blob transactions when Cancun is not active for the block timestamp. Verification notes: The patch shows missing fork-specific validation, but does not by itself prove remote exploitability. The evidence does not prove that invalid pre-Cancun blob payloads were ever accepted into canonical state. The patch does not establish a demonstrated consensus split; it only shows enforcement of a consensus-rule boundary. The exact RPC/error-code interoperability impact is suggested by comments, but not fully proven from the excerpt alone. No test diff or runtime trace was provided. The supplied excerpts show the new rejection path, but not a full pre-patch execution proving acceptance of pre-Cancun blob payloads. No evidence here demonstrates exploitation, chain impact, or a consensus split. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-rule-validation`
Final impact type: `consensus-integrity, protocol-input-validation`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, engine-api, payload-validation, fork-gating, blob-transactions`

The patch clearly tightens a consensus-sensitive validation path by explicitly rejecting blob transactions in pre-Cancun payloads and by routing that case through a distinct error path before block-hash validation. In a blockchain execution/consensus boundary, missing fork-gated payload checks are security-relevant because they affect protocol rule enforcement. However, the provided evidence does not prove a concrete exploitable acceptance path, canonical state corruption, or an observed consensus split, so this is better retained as security hardening rather than a confirmed security bug fix.

## Security Evidence

1. `ensure_well_formed_payload` now documents and enforces that pre-Cancun blocks must not contain blob transactions.
2. The new check gates behavior on `is_cancun_active_at_timestamp(block.timestamp)` and `block.has_blob_transactions()`, showing fork-rule enforcement.
3. The rejection happens before block-hash validation, indicating deliberate handling of a protocol-invalid input class.
4. The function signature changes to separate `PayloadStatus` handling from `BeaconOnNewPayloadError`, showing a new explicit invalid-input path in the engine API boundary.
5. The touched code is in beacon consensus / engine payload validation, a security-sensitive protocol path.

## Missing Evidence

1. No pre-patch execution trace proves such payloads were previously accepted through to canonical processing.
2. No test or runtime evidence shows a consensus split, chain halt, or remotely triggerable exploit.
3. The excerpts do not show downstream state transition effects from the old behavior.
4. The exact external attack surface and peer/RPC reachability are not established from the patch alone.

## Claim Boundaries

1. Supported claim: the commit adds missing fork-aware validation for pre-Cancun payload contents.
2. Supported claim: the change hardens a consensus-sensitive engine API path against malformed or disallowed payloads.
3. Not supported: that this caused state corruption, database corruption, or confirmed canonical chain acceptance.
4. Not supported: that exploitation occurred or that a concrete consensus failure was observed.
5. Not supported: classification as a fully proven security-fix rather than security-hardening.
