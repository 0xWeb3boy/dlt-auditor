---
case_id: case_20260416_aafd24614
project: base
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2026-04-16
source_refs:
  - git:aafd24614d6a987a3222218bbee41783ba4285ce
  - "crates/infra/audit/src/storage.rs:237"
  - "crates/infra/audit/src/storage.rs:401"
  - "crates/infra/audit/src/storage.rs:26"
  - "crates/infra/audit/src/storage.rs:165"
bug_class: audit-log-integrity
impact_type:
  - integrity-loss
  - event-loss
confidence: medium
tags:
  - audit
  - s3
  - write-once
  - idempotency
  - concurrency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The diff shows an audit-storage design change from rewriting one mutable per-bundle S3 object to storing immutable per-event objects with conditional write-once semantics and reconstructing history by listing those objects. That supports a storage-integrity and concurrency-hardening interpretation, but the provided evidence does not establish a concrete exploitable vulnerability or attacker-triggered security flaw.

## Observed Patch Facts

1. In `crates/infra/audit/src/storage.rs`, the patch replaces `async fn update_bundle_history(&self, event: Event) -> Result<()> {` with `/// Writes a single event object to S3 with write-once semantics.`.

2. In `crates/infra/audit/src/storage.rs`, the patch replaces `let s3_key = S3Key::Bundle(bundle_id).to_string();` with `/// Reconstructs a bundle's full history by listing all event objects`.

3. In `crates/infra/audit/src/storage.rs`, the patch replaces `/// S3 key types for storing different event types.` with `/// Maximum number of retries for transient S3 errors (not conflicts).`.

4. In `crates/infra/audit/src/storage.rs`, the patch replaces `fn update_bundle_history_transform(` with `/// Converts a ['BundleEvent'] and its metadata into a ['BundleHistoryEvent'] for sto...`.

## Project Context

The changed code sits primarily in `crates/infra/audit/src`, `crates/infra/audit`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/infra/audit/src/lib.rs`, `crates/infra/audit/src/types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/infra/audit/src/lib.rs`, `crates/infra/audit/src/types.rs`. The strongest project-level identifiers around this patch are `event`, `bundle_id`, `S3Key::Bundle`, and `BundleHistory`. Nearby tests or test-like files include `crates/infra/audit/tests/s3_test.rs`, `crates/infra/audit/tests/integration_tests.rs`.

## Before/After Behavior

Before the patch, bundle history was read from and updated through a single `S3Key::Bundle(bundle_id)` object, with history assembled in memory and written back. After the patch, each event is written as its own S3 object via `write_once` using `If-None-Match: *`, duplicate `412` responses are treated as success, and `get_bundle_history` reconstructs history by listing keys under the bundle prefix and sorting the resulting events.

# Root Cause

The evidence suggests the old design used read-modify-write updates against one shared bundle-history object in S3, which the new comments describe as creating read-modify-write contention. The patch addresses that by making each event an immutable record with write-once semantics, but the excerpts do not prove a specific pre-patch failure beyond that contention risk.

## Walkthrough

1. `storage.rs` previously updated bundle history through `update_bundle_history`, deriving `S3Key::Bundle(bundle_id)` and mutating a stored `BundleHistory` object.

2. The old read path for `get_bundle_history` fetched that same single object with `get_object_with_etag::<BundleHistory>(&s3_key)`, so one S3 object represented the bundle's full history.

3. The patch adds `write_once`, documented to use `If-None-Match: *`, return success on duplicate `412` responses, and retry only transient S3 failures.

4. Comments on `S3Key` now state that each event is stored as its own object to avoid read-modify-write contention.

5. The archive path writes the bundle event separately and performs transaction index writes alongside it.

6. The new `get_bundle_history` lists keys under `bundles/{bundle_id}/`, returns `None` when empty, and reconstructs history from per-event objects sorted by timestamp.

7. These changes support a conclusion that the patch hardens storage consistency under retries or contention, but they do not by themselves prove a security vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/infra/audit/src/storage.rs | 165 | Bundle history event identity/dedup path keyed by event key before assembly into stored history |
| crates/infra/audit/src/storage.rs | 237 | S3 event write path adding write-once conditional PUT semantics and transient-only retry behavior |
| crates/infra/audit/src/storage.rs | 381 | Archive flow that persists bundle events and related transaction indexes |
| crates/infra/audit/src/storage.rs | 401 | Bundle history read path changed to reconstruct history from per-event objects under a bundle prefix |

## Code Snippets

## Snippet 1

Context: `crates/infra/audit/src/storage.rs:237` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    async fn update_bundle_history(&self, event: Event) -> Result<()> {
        let s3_key = S3Key::Bundle(event.event.bundle_id()).to_string();

        self.idempotent_write::<BundleHistory, _>(&s3_key, |current_history| {
            update_bundle_history_transform(current_history, &event)
        })
```
After
```rust
}

    /// Writes a single event object to S3 with write-once semantics.
    ///
    /// Uses `If-None-Match: *` so that only the first PUT for a given key
    /// succeeds. Returns `Ok(())` for both successful writes and duplicate
    /// 412 responses. Only retries on transient S3 errors (5xx, timeouts).
    async fn write_once(&self, key: &str, body: &[u8]) -> Result<()> {
```

## Snippet 2

Context: `crates/infra/audit/src/storage.rs:401` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
#[async_trait]
impl BundleEventS3Reader for S3EventReaderWriter {
    async fn get_bundle_history(&self, bundle_id: BundleId) -> Result<Option<BundleHistory>> {
        let s3_key = S3Key::Bundle(bundle_id).to_string();
        let (bundle_history, _) = self.get_object_with_etag::<BundleHistory>(&s3_key).await?;
        Ok(bundle_history)
    }
```
After
```rust
#[async_trait]
impl BundleEventS3Reader for S3EventReaderWriter {
    /// Reconstructs a bundle's full history by listing all event objects
    /// under `bundles/{bundle_id}/` and assembling them sorted by timestamp.
    async fn get_bundle_history(&self, bundle_id: BundleId) -> Result<Option<BundleHistory>> {
        let prefix = S3Key::BundlePrefix(bundle_id).to_string();
        let keys = self.list_keys(&prefix).await?;
```

## Snippet 3

Context: `crates/infra/audit/src/storage.rs:26` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
};

/// S3 key types for storing different event types.
#[derive(Debug)]
pub enum S3Key {
    /// Key for bundle events.
    Bundle(BundleId),
    /// Key for transaction lookups by hash.
```
After
```rust
};

/// Maximum number of retries for transient S3 errors (not conflicts).
const MAX_TRANSIENT_RETRIES: usize = 3;

/// Base delay in milliseconds between transient error retries.
const TRANSIENT_RETRY_BASE_DELAY_MS: u64 = 100;
```

## Snippet 4

Context: `crates/infra/audit/src/storage.rs:165` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

fn update_bundle_history_transform(
    bundle_history: BundleHistory,
    event: &Event,
) -> Option<BundleHistory> {
    let mut history = bundle_history.history;
    let bundle_id = event.event.bundle_id();
```
After
```rust
}

/// Converts a [`BundleEvent`] and its metadata into a [`BundleHistoryEvent`] for storage.
fn into_history_event(event: &Event) -> BundleHistoryEvent {
    match &event.event {
        BundleEvent::Received { bundle, .. } => BundleHistoryEvent::Received {
            key: event.key.clone(),
```

# Fix Pattern

Replace mutable aggregate-object updates with immutable per-event records, enforce write-once storage for each event key, treat duplicate deliveries as no-ops, and rebuild aggregate history by enumerating stored events.

## How It Was Fixed

The write path now stores each event as its own S3 object through `write_once` and uses conditional PUT semantics so only the first write for a key succeeds. Duplicate writes that hit `412` are accepted as benign duplicates, while retries are limited to transient S3 errors. The read path no longer trusts a single mutable history object; it lists all event objects for a bundle and reconstructs `BundleHistory` from those records.

# Why It Matters

1. Reduces the chance that one rewrite of shared history drops earlier events.

2. Makes duplicate event delivery behave as a no-op instead of a conflicting update path.

3. Moves audit history closer to append-only event-log behavior.

4. Improves storage consistency, but exploitability is not shown by the excerpts.

# Evidence Notes

Grounded evidence is limited to the provided `storage.rs` excerpts and the fact that `crates/infra/audit/tests/s3_test.rs` changed. The strongest direct support is the new `write_once` documentation, the comment that each event is stored separately to avoid read-modify-write contention, and the read-path change from loading one bundle object to listing a bundle prefix. The provided material does not show an attacker model, a demonstrated overwrite bug in production, authorization impact, cryptographic impact, or any direct confidentiality/integrity breach beyond the storage-consistency concern implied by the redesign. Protocol security invariant: Audit history storage should preserve each bundle event exactly once and reconstruct complete history without losing prior events when writes are retried or occur concurrently. Verification notes: The patch does not prove an external attacker could trigger or exploit the prior behavior. The patch does not show unauthorized S3 writes or a permission bypass. The patch does not demonstrate cryptographic breakage; the issue is storage integrity and concurrency semantics. The patch does not prove funds loss or consensus impact. The evidence does not establish whether the old implementation was already causing production data loss, only that the new design avoids that class of contention. The provided excerpts support the storage-model change but not a confirmed exploit path. A test file was updated, but the exact assertions were not provided here. Security relevance is plausible because audit integrity matters, but the vulnerability thesis is not established from the supplied evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `audit-log-integrity`
Final impact type: `integrity-loss, event-loss`
Final confidence: `medium`
Final tags: `audit, s3, write-once, idempotency, concurrency`

The patch is best read as security hardening for an audit-storage path, not as a confirmed security bug fix. The evidence shows a shift from mutable read-modify-write bundle history updates to immutable per-event objects with S3 conditional write-once semantics, duplicate suppression, and history reconstruction from append-only records. In an audit subsystem, that materially strengthens integrity guarantees and reduces the risk of lost or conflicting history under retries or concurrent writes. However, the supplied patch does not prove a concrete exploitable vulnerability, attacker trigger, authorization failure, or demonstrated integrity breach before the change.

## Security Evidence

1. Code is in the audit storage subsystem, where history integrity is security-sensitive.
2. New `write_once` path uses `If-None-Match: *` to enforce first-write-wins semantics.
3. Duplicate `412` responses are treated as benign duplicates rather than rewriting shared state.
4. Comments state each event is stored separately to avoid read-modify-write contention.
5. Read path now reconstructs history from per-event objects instead of trusting one mutable aggregate object.

## Missing Evidence

1. No proof that an attacker could influence or exploit the prior contention behavior.
2. No demonstrated pre-patch loss, overwrite, or tampering of audit history.
3. No authorization, confidentiality, or privilege-boundary change is shown.
4. Test assertions are not provided, so the exact failure mode is not visible.

## Claim Boundaries

1. This supports an audit-integrity hardening interpretation, not a confirmed exploitable security vulnerability.
2. The patch evidence is about storage semantics and concurrency behavior, not cryptographic breakage or access control.
3. Retention in the corpus is justified only as a security-hardening case tied to audit log integrity.
