---
case_id: case_20220826_c846221bb8
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-08-26
source_refs:
  - git:c846221bb8611dba3f257d8403a8dde233a8655b
  - "runtime/src/accounts_background_service.rs:278"
  - "runtime/src/snapshot_utils.rs:1618"
  - "runtime/src/snapshot_utils.rs:209"
  - "runtime/src/snapshot_utils.rs:28"
bug_class: missing-snapshot-validation
impact_type:
  - state-integrity
confidence: medium
tags:
  - runtime
  - snapshot
  - snapshot-validation
  - state-integrity
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds validation for snapshot slot deltas during Solana snapshot restoration. It inserts `verify_slot_deltas(slot_deltas.as_slice(), &bank)?` before `bank.src.append(&slot_deltas)`, adds a dedicated `SnapshotError::VerifySlotDeltas` error, imports slot-history checking support, and treats this validation failure as fatal. The evidence supports a snapshot restore integrity check, but does not establish a security vulnerability, attacker control, remote exploitability, consensus impact, or fund-loss risk.

## Observed Patch Facts

1. In `runtime/src/accounts_background_service.rs`, the patch adds `SnapshotError::VerifySlotDeltas(..) => true,`.

2. In `runtime/src/snapshot_utils.rs`, the patch replaces `fn get_snapshot_file_name(slot: Slot) -> String {` with `/// Verify that the snapshot's slot deltas are not corrupt/invalid`.

3. In `runtime/src/snapshot_utils.rs`, the patch replaces `/// If the validator halts in the middle of 'archive_snapshot_package()', the tempora...` with `#[error("snapshot slot deltas are invalid: {0}")]`.

4. In `runtime/src/snapshot_utils.rs`, the patch replaces `solana_sdk::{clock::Slot, genesis_config::GenesisConfig, hash::Hash, pubkey::Pubkey},` with `solana_sdk::{`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/serde_snapshot.rs`, `runtime/src/cost_tracker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/serde_snapshot.rs`, `runtime/src/cost_tracker.rs`. The strongest project-level identifiers around this patch are `std::result::Result`, `clock::Slot`, `genesis_config::GenesisConfig`, and `hash::Hash`.

## Before/After Behavior

Before the patch, the provided evidence shows slot deltas being appended into the rebuilt bank without an observed preceding slot-delta validation step. After the patch, snapshot restoration validates the deltas structurally and against the bank's slot history before append; validation failures are represented as `SnapshotError::VerifySlotDeltas` and treated as fatal during snapshot handling.

# Root Cause

The pre-fix behavior lacked an observed guard ensuring deserialized snapshot slot deltas were valid and consistent with the rebuilt bank before incorporation into restored state. The evidence does not show whether malformed deltas could be attacker-supplied or what security impact would follow.

## Walkthrough

1. Snapshot restoration rebuilds a `Bank` and obtains `slot_deltas` from snapshot data.

2. The pre-fix evidence shows `bank.src.append(&slot_deltas)` without a shown validation call immediately beforehand.

3. The patch inserts `verify_slot_deltas(slot_deltas.as_slice(), &bank)?` before the append.

4. The new validation performs structural checks using the rebuilt bank slot.

5. It then checks the resulting slots against `bank.get_slot_history()`.

6. Validation failure is converted into `SnapshotError::VerifySlotDeltas`.

7. The accounts background service classifies that error as fatal, causing invalid slot deltas to abort snapshot handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/snapshot_utils.rs | 1612 | calls `verify_slot_deltas` before appending deserialized slot deltas into the rebuilt bank |
| runtime/src/snapshot_utils.rs | 1618 | defines slot-delta validation against structural checks and bank slot history |
| runtime/src/snapshot_utils.rs | 209 | adds `SnapshotError::VerifySlotDeltas` to represent invalid snapshot slot deltas |
| runtime/src/accounts_background_service.rs | 265 | treats slot-delta verification failure as fatal snapshot handling error |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts_background_service.rs:278` (changes a sensitive control or state-update path)

Before
```rust
SnapshotError::NoSnapshotArchives => true,
            SnapshotError::MismatchedSlotHash(..) => true,
        }
    }
```
After
```rust
SnapshotError::NoSnapshotArchives => true,
            SnapshotError::MismatchedSlotHash(..) => true,
            SnapshotError::VerifySlotDeltas(..) => true,
        }
    }
```

## Snippet 2

Context: `runtime/src/snapshot_utils.rs:1618` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

fn get_snapshot_file_name(slot: Slot) -> String {
    slot.to_string()
```
After
```rust
}

/// Verify that the snapshot's slot deltas are not corrupt/invalid
fn verify_slot_deltas(
    slot_deltas: &[BankSlotDelta],
    bank: &Bank,
) -> std::result::Result<(), VerifySlotDeltasError> {
    let info = verify_slot_deltas_structural(slot_deltas, bank.slot())?;
```

## Snippet 3

Context: `runtime/src/snapshot_utils.rs:209` (changes a sensitive control or state-update path)

Before
```rust
#[error("snapshot has mismatch: deserialized bank: {:?}, snapshot archive info: {:?}", .0, .1)]
    MismatchedSlotHash((Slot, Hash), (Slot, Hash)),
}
pub type Result<T> = std::result::Result<T, SnapshotError>;

/// If the validator halts in the middle of `archive_snapshot_package()`, the temporary staging
/// directory won't be cleaned up.  Call this function to clean them up.
```
After
```rust
#[error("snapshot has mismatch: deserialized bank: {:?}, snapshot archive info: {:?}", .0, .1)]
    MismatchedSlotHash((Slot, Hash), (Slot, Hash)),

    #[error("snapshot slot deltas are invalid: {0}")]
    VerifySlotDeltas(#[from] VerifySlotDeltasError),
}
pub type Result<T> = std::result::Result<T, SnapshotError>;
```

## Snippet 4

Context: `runtime/src/snapshot_utils.rs:28` (changes signature or replay validation logic)

Before
```rust
regex::Regex,
    solana_measure::measure::Measure,
    solana_sdk::{clock::Slot, genesis_config::GenesisConfig, hash::Hash, pubkey::Pubkey},
    std::{
        cmp::{max, Ordering},
```
After
```rust
regex::Regex,
    solana_measure::measure::Measure,
    solana_sdk::{
        clock::Slot,
        genesis_config::GenesisConfig,
        hash::Hash,
        pubkey::Pubkey,
        slot_history::{Check, SlotHistory},
```

# Fix Pattern

Validate snapshot-derived metadata before mutating restored runtime state, propagate a dedicated validation error, and make that error fatal in snapshot handling.

## How It Was Fixed

The change adds `verify_slot_deltas`, calls it before appending slot deltas to the rebuilt bank, introduces `VerifySlotDeltasError` and `SnapshotError::VerifySlotDeltas`, imports `slot_history::{Check, SlotHistory}`, and updates fatal snapshot error classification to include slot-delta verification failures.

# Why It Matters

1. Prevents corrupt or invalid snapshot slot deltas from being appended during restore.

2. Improves integrity checks in snapshot loading.

3. Makes invalid slot-delta handling explicit and fatal.

4. Security impact is not proven by the provided evidence.

# Evidence Notes

Grounded evidence is limited to `runtime/src/snapshot_utils.rs` and `runtime/src/accounts_background_service.rs`. The strongest supported claim is that snapshot slot deltas are newly validated before append during bank rebuild. The evidence does not show who controls snapshot archives, whether malformed slot deltas are reachable through an adversarial path, or whether acceptance would cause consensus divergence, fund loss, privilege bypass, or another concrete security impact. Protocol security invariant: When rebuilding a bank from snapshot archives, slot deltas should be structurally valid, bounded, and consistent with the rebuilt bank's rooted slot history before being appended into restored runtime state. Verification notes: The patch does not prove remote exploitability. The patch does not show who can supply the malformed snapshot archive. The patch does not show consensus divergence or fund loss directly. The patch does not indicate a cryptographic primitive failure. The touched path is snapshot loading/restoration, not normal transaction execution. No external context or file inspection was used. Mapper's transaction-processing framing is unsupported; the affected path is snapshot loading/restoration. Mapper's `likely` security verdict is stronger than the provided evidence supports. Keep out of the security corpus unless additional evidence establishes attacker reachability or concrete protocol impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-snapshot-validation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `runtime, snapshot, snapshot-validation, state-integrity, security-hardening`

The patch clearly adds validation of deserialized snapshot slot deltas before appending them into restored bank state, introduces a dedicated validation error, and makes that error fatal. The supplied evidence does not prove attacker control or a concrete exploit, so this should not be treated as a confirmed security fix, but it is reasonable security hardening for a state-integrity-sensitive snapshot restoration path.

## Security Evidence

1. Adds `verify_slot_deltas(slot_deltas.as_slice(), &bank)?` before `bank.src.append(&slot_deltas)` during snapshot bank rebuild.
2. New validation checks snapshot slot deltas for corruption/invalidity and compares them against bank slot history.
3. Adds `SnapshotError::VerifySlotDeltas` for invalid snapshot slot deltas.
4. Classifies `SnapshotError::VerifySlotDeltas(..)` as fatal in snapshot error handling.

## Missing Evidence

1. No evidence that malformed snapshot archives are attacker-controlled or remotely supplied.
2. No demonstrated consensus divergence, fund loss, privilege bypass, or denial-of-service impact.
3. No advisory, CVE, exploit description, or security note is provided.
4. No before/after test evidence showing the prior behavior accepted malicious data.

## Claim Boundaries

1. Validate as security hardening, not a concrete security fix.
2. The supported bug class is missing snapshot validation, not proven exploitable state corruption.
3. The affected path is snapshot loading/restoration, not normal transaction processing.
4. Do not claim remote exploitability, cryptographic failure, or fund-loss impact from the supplied evidence alone.
