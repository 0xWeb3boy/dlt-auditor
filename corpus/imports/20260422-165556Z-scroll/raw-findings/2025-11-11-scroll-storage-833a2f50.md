---
case_id: case_20251111_833a2f50
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2025-11-11
source_refs:
  - git:833a2f50a5e3fa8063b8c02b321bb9e1606f0f57
  - "crates/libzkp_c/src/lib.rs:160"
  - "coordinator/internal/utils/codec_validium.go:19"
  - "coordinator/internal/logic/submitproof/proof_receiver.go:220"
bug_class: key-material-handling
impact_type:
  - information-disclosure
confidence: medium
tags:
  - blockchain-core
  - secret-handling
  - sensitive-logging
  - ffi-input-validation
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a likely security-hardening change in the validium proof path. The patch removes logging of `chunkProof.MetaData.ChunkInfo.EncryptionKey` and replaces an `assert_eq!` on `decryption_key_len` in an `unsafe extern "C"` entrypoint with explicit validation and a failure return. The `codec_validium.go` schema change is adjacent protocol work, but the supplied evidence does not establish it as a proven vulnerability fix.

## Observed Patch Facts

1. In `crates/libzkp_c/src/lib.rs`, the patch replaces `assert_eq!(decryption_key_len, 32, "len(decryption_key) != 32");` with `if decryption_key_len != 32 {`.

2. In `coordinator/internal/utils/codec_validium.go`, the patch replaces `Version CodecVersion 'json:"version"'` with `Version CodecVersion 'json:"version"'`.

3. In `coordinator/internal/logic/submitproof/proof_receiver.go`, the patch removes `log.Info("parse chunkproof", "key", chunkProof.MetaData.ChunkInfo.EncryptionKey)`.

## Project Context

The changed code sits primarily in `crates/libzkp_c/src`, `crates/libzkp_c`, `coordinator/internal/utils`, which anchors the finding in the `storage` area of the project. Historical context from `coordinator/internal/utils/version.go`, `coordinator/internal/utils/prover_name.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `coordinator/internal/types/auth.go`, `coordinator/internal/orm/prover_task.go`. The strongest project-level identifiers around this patch are `json`, `common`, `Hash`, and `decryption_key_len`.

## Before/After Behavior

Before the patch, chunk-proof handling logged an `EncryptionKey` field during proof processing, and `gen_universal_task` enforced `decryption_key_len == 32` with `assert_eq!` before using the raw pointer. After the patch, the log line is removed, and `gen_universal_task` checks the length explicitly, emits an error, and returns `failed_handling_result()` when the key length is not 32. The validium batch struct also changes from `BlobVersionedHash` to `Commitment`, but the evidence only shows a serialization/protocol update, not a demonstrated security flaw.

# Root Cause

The grounded issue is inconsistent handling of key material at sensitive boundaries: an encryption key was treated as loggable data in proof submission, and an unsafe FFI path relied on an assertion rather than a normal fail-closed validation path for decryption-key length. The separate codec struct change is not sufficiently tied by the provided evidence to the same root cause.

## Walkthrough

1. `HandleZkProof` unmarshals a chunk proof and, before the patch, logged `chunkProof.MetaData.ChunkInfo.EncryptionKey` before verification.

2. The patch deletes that log statement, so the same proof-handling path no longer emits the key value.

3. `gen_universal_task` is an `unsafe extern "C"` entrypoint that accepts a raw `decryption_key` pointer and `decryption_key_len`.

4. Before the patch, when a key was present, the code used `assert_eq!(decryption_key_len, 32, ...)` before constructing a slice from the raw pointer.

5. After the patch, the function checks `if decryption_key_len != 32`, logs an error, and returns `failed_handling_result()` instead of asserting.

6. `failed_handling_result()` sets `ok` false and returns null task and metadata pointers, showing an ordinary handled failure path.

7. Separately, `daBatchValidiumV1` replaces `BlobVersionedHash` with `Commitment`, but the provided material does not show that this change fixes incorrect proof acceptance, replay, or forgery.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/libzkp_c/src/lib.rs | 160 | unsafe universal-task generator now rejects non-32-byte decryption keys by returning a failure result instead of asserting |
| coordinator/internal/logic/submitproof/proof_receiver.go | 220 | proof receiver no longer logs the chunk proof encryption key during proof handling |
| coordinator/internal/utils/codec_validium.go | 19 | validium DA batch serialization schema changes around commitment/blob-hash fields |

## Code Snippets

## Snippet 1

Context: `crates/libzkp_c/src/lib.rs:160` (changes the branch that decides whether execution stops or continues)

Before
```rust
let cli = l2geth::get_client();
        let decryption_key = if decryption_key_len > 0 {
            assert_eq!(decryption_key_len, 32, "len(decryption_key) != 32");
            Some(std::slice::from_raw_parts(
                decryption_key,
```
After
```rust
let cli = l2geth::get_client();
        let decryption_key = if decryption_key_len > 0 {
            if decryption_key_len != 32 {
                tracing::error!(
                    "gen_universal_task received {}-byte decryption key; expected 32",
                    decryption_key_len
                );
                return failed_handling_result();
```

## Snippet 2

Context: `coordinator/internal/utils/codec_validium.go:19` (changes signature or replay validation logic)

Before
```go
type daBatchValidiumV1 struct {
	Version           CodecVersion `json:"version"`
	BatchIndex        uint64       `json:"batch_index"`
	BlobVersionedHash common.Hash  `json:"blob_versioned_hash"`
	ParentBatchHash   common.Hash  `json:"parent_batch_hash"`
	PostStateRoot     common.Hash  `json:"post_state_root"`
	WithDrawRoot      common.Hash  `json:"withdraw_root"`
```
After
```go
type daBatchValidiumV1 struct {
	Version         CodecVersion `json:"version"`
	BatchIndex      uint64       `json:"batch_index"`
	ParentBatchHash common.Hash  `json:"parent_batch_hash"`
	PostStateRoot   common.Hash  `json:"post_state_root"`
	WithDrawRoot    common.Hash  `json:"withdraw_root"`
	Commitment      common.Hash  `json:"commitment"`
```

## Snippet 3

Context: `coordinator/internal/logic/submitproof/proof_receiver.go:220` (changes a sensitive control or state-update path)

Before
```go
return unmarshalErr
		}
		log.Info("parse chunkproof", "key", chunkProof.MetaData.ChunkInfo.EncryptionKey)
		success, verifyErr = m.verifier.VerifyChunkProof(chunkProof, hardForkName)
		if stat := chunkProof.VmProof.Stat; stat != nil {
```
After
```go
return unmarshalErr
		}
		success, verifyErr = m.verifier.VerifyChunkProof(chunkProof, hardForkName)
		if stat := chunkProof.VmProof.Stat; stat != nil {
```

# Fix Pattern

Remove sensitive-value logging and replace assertion-based boundary checks with explicit validation and handled failure.

## How It Was Fixed

The fix removes the proof-receiver log line that printed the chunk proof's encryption key. It also changes the Rust FFI boundary from `assert_eq!`-based enforcement of a 32-byte decryption key to an explicit runtime check that returns `failed_handling_result()` on mismatch. The validium codec struct is updated in the same commit, but that part is best treated as adjacent protocol or serialization alignment rather than a validated security fix from the supplied evidence.

# Why It Matters

1. It stops emitting key material during normal proof handling.

2. It makes malformed key length a handled error instead of an assertion-triggered failure.

3. It is safer to validate untrusted boundary inputs explicitly at an unsafe FFI interface.

4. The codec change may matter for protocol correctness, but that security significance is not proven here.

# Evidence Notes

The strongest evidence is the deleted `log.Info(..., "key", chunkProof.MetaData.ChunkInfo.EncryptionKey)` call and the replacement of `assert_eq!(decryption_key_len, 32, ...)` with an explicit length check plus `failed_handling_result()`. Those changes directly support a key-handling hardening interpretation. The `codec_validium.go` diff clearly changes serialized fields, but the provided excerpts do not establish a prior exploitable security condition or show that the struct edit is the root of the fix. Protocol security invariant: Proof-processing code should not expose encryption or decryption keys in logs, and the unsafe C/Rust task-generation boundary should accept key material only in the expected 32-byte form and otherwise return a handled failure. Verification notes: The patch does not prove that malformed `decryption_key_len` is remotely reachable by an untrusted attacker. The patch does not show whether prior key logging reached untrusted log consumers or only internal operators. The `codec_validium.go` change may be protocol-correctness cleanup; the diff alone does not prove a forgery or replay vulnerability. The patch does not establish that any past proofs were accepted incorrectly or that key material was actively exfiltrated. Direct code evidence shows removal of logging for an `EncryptionKey` field. Direct code evidence shows fail-closed handling for non-32-byte `decryption_key_len`. The provided excerpts do not establish whether the old assertion path was attacker-reachable. The provided excerpts do not establish who could read the old logs. The `codec_validium.go` change is real but not sufficient on its own to prove a vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `key-material-handling`
Final impact type: `information-disclosure`
Final confidence: `medium`
Final tags: `blockchain-core, secret-handling, sensitive-logging, ffi-input-validation`

The patch directly supports a security-hardening interpretation, but not the original state-corruption claim. Two concrete changes tighten handling of sensitive key material: proof processing stops logging an `EncryptionKey`, and an `unsafe extern "C"` boundary now rejects malformed decryption-key lengths through a normal failure path instead of asserting. That is enough to retain this as a security-focused hardening case, but the provided evidence does not prove an exploitable vulnerability, attacker reachability, or any state-integrity failure. The `codec_validium.go` schema change looks like adjacent protocol work rather than validated security evidence from the patch alone.

## Security Evidence

1. The patch removes logging of `chunkProof.MetaData.ChunkInfo.EncryptionKey` in proof handling.
2. The removed field is explicitly named `EncryptionKey`, which is sensitive material by nature.
3. The Rust FFI entrypoint is `unsafe extern "C"` and now validates `decryption_key_len` explicitly.
4. Malformed key length now returns `failed_handling_result()` instead of triggering `assert_eq!`.
5. The new behavior is fail-closed for unexpected decryption-key length values.

## Missing Evidence

1. No evidence shows who could access the old logs or whether the logged key was exposed externally.
2. No evidence proves malformed `decryption_key_len` was attacker-controlled or remotely reachable.
3. No evidence shows the prior assertion caused exploitable crashes in production.
4. No evidence ties the `codec_validium.go` field change to proof forgery, replay, or incorrect acceptance.
5. No tests, advisory text, or commit message explain a concrete security incident or vulnerability.

## Claim Boundaries

1. This supports security hardening around secret handling and boundary validation, not a proven exploit fix.
2. The evidence does not support the original `state-corruption` / `state-integrity` classification.
3. The `codec_validium.go` change should not be treated as validated security evidence from this patch alone.
4. The safest retained claim is reduced secret exposure in logs plus stricter fail-closed key-length handling.
