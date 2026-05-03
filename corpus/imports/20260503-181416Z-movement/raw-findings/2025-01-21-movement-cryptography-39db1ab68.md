---
case_id: case_20250121_39db1ab68
project: movement
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2025-01-21
source_refs:
  - git:39db1ab68e6777bacb1a8d780a8b42d34d11ce30
  - "protocol-units/da/movement/celestia/util/src/ir_blob.rs:211"
  - "protocol-units/da/movement/celestia/util/src/ir_blob.rs:121"
  - "protocol-units/da/movement/celestia/util/src/ir_blob.rs:46"
  - "protocol-units/da/movement/celestia/light-node-verifier/src/permissioned_signers/mod.rs:70"
bug_class: input-validation
impact_type:
  - availability-hardening
confidence: medium
tags:
  - validator-ops
  - cryptography
  - input-validation
  - resource-control
  - blob-size-limit
  - signature-validation
  - panic-avoidance
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The strongest grounded finding is a likely Celestia DA resource-control fix. `InnerSignedBlobV1Data::new` was replaced with fallible `try_new`, which rejects blobs larger than `MAX_BLOB_LEN`. This aligns with the commit title, "Zstd bomb fix", but the supplied evidence does not show the decompression code itself. The same file also adds a signature-length check and a regression test for wrong-length signatures not panicking; that is supported as input-validation hardening, but it is separate from the zstd-bomb thesis.

## Observed Patch Facts

1. In `protocol-units/da/movement/celestia/util/src/ir_blob.rs`, the patch replaces `pub mod celestia {` with `#[test]`.

2. In `protocol-units/da/movement/celestia/util/src/ir_blob.rs`, the patch adds `if self.signature.len() != SignatureSize::<C>::to_usize() {`.

3. In `protocol-units/da/movement/celestia/util/src/ir_blob.rs`, the patch replaces `pub fn new(blob: Vec<u8>, timestamp: u64) -> Self {` with `pub fn try_new(blob: Vec<u8>, timestamp: u64) -> Result<Self, anyhow::Error> {`.

4. In `protocol-units/da/movement/celestia/light-node-verifier/src/permissioned_signers/mod.rs`, the patch replaces `async fn verify(&self, blob: CelestiaBlob, height: u64) -> Result<Verified<Intermedia...` with `async fn verify(`.

## Project Context

The changed code sits primarily in `protocol-units/da/movement/celestia/util/src`, `protocol-units/da/movement/celestia/util`, `protocol-units/da/movement/celestia/light-node-verifier/src/permissioned_signers`, which anchors the finding in the `cryptography` area of the project. Historical context from `protocol-units/da/movement/celestia/util/src/lib.rs`, `protocol-units/da/movement/celestia/light-node-verifier/src/v1.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/da/movement/celestia/light-node-verifier/src/v1.rs`, `protocol-units/da/movement/celestia/light-node-verifier/src/celestia/mod.rs`. The strongest project-level identifiers around this patch are `blob`, `anyhow::Error`, `signature`, and `anyhow`.

## Before/After Behavior

Before the patch, the provided evidence shows `InnerSignedBlobV1Data::new(blob, timestamp)` constructing `Self { blob, timestamp }` with no visible maximum-size validation. After the patch, `try_new(blob, timestamp) -> Result<Self, anyhow::Error>` rejects `blob.len() > MAX_BLOB_LEN`. Before the patch, `InnerSignedBlobV1::try_verify` passed `self.signature.as_slice().into()` directly to `ecdsa::Signature::from_bytes`. After the patch, it first checks `self.signature.len()` against `SignatureSize::<C>::to_usize()` and returns `invalid signature length` on mismatch. The permissioned signer verifier hunk is only formatting context in the supplied evidence.

# Root Cause

The supported root cause is missing validation at blob and signature parsing boundaries. Blob data could be wrapped into `InnerSignedBlobV1Data` without the visible `MAX_BLOB_LEN` guard, allowing oversized decoded data to enter downstream processing. Separately, arbitrary-length signature bytes could reach ECDSA signature parsing before an explicit size check.

## Walkthrough

1. Celestia DA blob data is represented through `InnerSignedBlobV1Data` in `ir_blob.rs`.

2. The old constructor accepted a `Vec<u8>` and timestamp and directly returned the data object in the supplied snippet.

3. The patch changes construction to `try_new` and rejects blobs larger than `MAX_BLOB_LEN`.

4. This provides the only direct evidence for the zstd-bomb/resource-exhaustion fix; decompression code is not shown.

5. Signed blob verification hashes blob data, timestamp, and id before ECDSA verification.

6. The old verification path converted signature bytes without a visible length guard.

7. The patch checks the curve-specific signature length before calling `ecdsa::Signature::from_bytes`.

8. A regression test constructs an empty signature and verifies the wrong-length path does not panic.

9. The verifier context places this code near Celestia DA light-node verification, but the excerpt does not show a behavior change there.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/da/movement/celestia/util/src/ir_blob.rs | 46 | Adds checked construction for InnerSignedBlobV1Data and rejects blobs larger than MAX_BLOB_LEN. |
| protocol-units/da/movement/celestia/util/src/ir_blob.rs | 109 | Verifies signed blob contents and now validates signature length before ECDSA Signature::from_bytes. |
| protocol-units/da/movement/celestia/util/src/ir_blob.rs | 211 | Regression test demonstrating malformed signature length returns an error instead of panicking. |
| protocol-units/da/movement/celestia/light-node-verifier/src/permissioned_signers/mod.rs | 64 | Business verification path for Celestia blobs before permissioned signer validation; provided hunk is mostly formatting context. |

## Code Snippets

## Snippet 1

Context: `protocol-units/da/movement/celestia/util/src/ir_blob.rs:211` (changes signature or replay validation logic)

Before
```rust
Ok(())
	}
}

pub mod celestia {

	use super::IntermediateBlobRepresentation;
	use anyhow::Context;
```
After
```rust
Ok(())
	}

	#[test]
	fn poc_verify_does_not_panic_on_wrong_signature_len() -> Result<(), anyhow::Error> {
		let s = InnerSignedBlobV1 {
			data: InnerSignedBlobV1Data::try_new(vec![1, 2, 3], 123).unwrap(),
			signature: vec![],
```

## Snippet 2

Context: `protocol-units/da/movement/celestia/util/src/ir_blob.rs:121` (changes signature or replay validation logic)

Before
```rust
let verifying_key = VerifyingKey::<C>::from_sec1_bytes(self.signer.as_slice())?;
		let signature = ecdsa::Signature::from_bytes(self.signature.as_slice().into())?;
```
After
```rust
let verifying_key = VerifyingKey::<C>::from_sec1_bytes(self.signer.as_slice())?;
		if self.signature.len() != SignatureSize::<C>::to_usize() {
			return Err(anyhow::anyhow!("invalid signature length"));
		}
		let signature = ecdsa::Signature::from_bytes(self.signature.as_slice().into())?;
```

## Snippet 3

Context: `protocol-units/da/movement/celestia/util/src/ir_blob.rs:46` (changes bounds, limits, or capacity handling)

Before
```rust
impl InnerSignedBlobV1Data {
	pub fn new(blob: Vec<u8>, timestamp: u64) -> Self {
		Self { blob, timestamp }
	}
```
After
```rust
impl InnerSignedBlobV1Data {
	pub fn try_new(blob: Vec<u8>, timestamp: u64) -> Result<Self, anyhow::Error> {
		if blob.len() > MAX_BLOB_LEN {
			bail!("blob length {} is above the limit", blob.len());
		}
		Ok(Self { blob, timestamp })
	}
```

## Snippet 4

Context: `protocol-units/da/movement/celestia/light-node-verifier/src/permissioned_signers/mod.rs:70` (changes signature or replay validation logic)

Before
```rust
FieldBytesSize<C>: ModulusSize,
{
	async fn verify(&self, blob: CelestiaBlob, height: u64) -> Result<Verified<IntermediateBlobRepresentation>, Error> {
		let verified_blob = self.celestia.verify(blob, height).await?;
		self.known_signers.verify(verified_blob.into_inner(), height).await
```
After
```rust
FieldBytesSize<C>: ModulusSize,
{
	async fn verify(
		&self,
		blob: CelestiaBlob,
		height: u64,
	) -> Result<Verified<IntermediateBlobRepresentation>, Error> {
		let verified_blob = self.celestia.verify(blob, height).await?;
```

# Fix Pattern

Replace unchecked construction and panic-prone parsing boundaries with fallible validation. Enforce a maximum decoded blob size before accepting blob data, and validate fixed-width signature encodings before cryptographic parsing.

## How It Was Fixed

`InnerSignedBlobV1Data::new` became `InnerSignedBlobV1Data::try_new`, returning `Result` and rejecting oversized blobs with `bail!`. `InnerSignedBlobV1::try_verify` now checks `self.signature.len()` against `SignatureSize::<C>::to_usize()` before ECDSA parsing. Tests were updated to use `try_new`, and a malformed-signature regression test was added.

# Why It Matters

1. Oversized decoded Celestia blob data is now rejected at construction time.

2. The evidence supports a likely resource-exhaustion fix, consistent with the commit title.

3. Malformed signature lengths are handled as ordinary errors instead of reaching a panic-prone conversion.

4. The evidence does not prove authentication bypass or remote exploitability.

# Evidence Notes

Primary support comes from `protocol-units/da/movement/celestia/util/src/ir_blob.rs`: the `MAX_BLOB_LEN` guard in `InnerSignedBlobV1Data::try_new`, the signature-length check in `try_verify`, and the `poc_verify_does_not_panic_on_wrong_signature_len` regression test. The zstd-bomb connection is supported by the commit title plus the new maximum blob-size guard, but not by direct decompression-code evidence. The `permissioned_signers` excerpt should be treated as subsystem context only because the visible hunk is formatting. Protocol security invariant: Celestia DA blob verification should reject decoded blob representations that exceed the configured maximum size before they are accepted into downstream signed-blob processing. Malformed fixed-size signature encodings should be rejected as validation errors rather than reaching panic-prone parsing paths. Verification notes: The provided evidence does not show the zstd decompression code directly. The patch does not prove a remotely triggerable node crash or resource exhaustion by itself. The permissioned_signers hunk does not show a behavioral change beyond formatting in the excerpt. The signature-length fix supports panic avoidance, but does not prove authentication bypass. No direct zstd decompression code is included in the supplied evidence. No exploit path or remote trigger is proven by the supplied evidence. The signature panic fix is supported by a regression test, but should not be merged into the resource-exhaustion root cause. The verifier hunk does not support an independent security claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `availability-hardening`
Final confidence: `medium`
Final tags: `validator-ops, cryptography, input-validation, resource-control, blob-size-limit, signature-validation, panic-avoidance`

The evidence supports retaining this as security hardening, not a fully proven security fix. The patch adds a maximum-size guard for blob data in a Celestia DA path and adds explicit signature-length validation with a regression test showing malformed signatures should error instead of panic. The commit title points to a zstd bomb, but the supplied patch evidence does not show decompression logic or a demonstrated remote exploit path, so remote DoS and concrete security-fix claims should be narrowed.

## Security Evidence

1. Commit subject is "Zstd bomb fix (#937)", indicating intended resource-exhaustion mitigation.
2. `InnerSignedBlobV1Data::try_new` now rejects `blob.len() > MAX_BLOB_LEN`.
3. `InnerSignedBlobV1::try_verify` now checks signature length before ECDSA signature parsing.
4. A regression test named `poc_verify_does_not_panic_on_wrong_signature_len` covers malformed signature length handling.
5. The changed code is in Celestia DA blob representation and verifier-adjacent cryptographic validation paths.

## Missing Evidence

1. No zstd decompression code is included in the supplied evidence.
2. No direct proof that oversized blobs were remotely attacker-controlled is shown.
3. No measured resource exhaustion, crash trace, or exploit scenario is provided.
4. The permissioned signer verifier hunk is formatting-only in the supplied evidence.

## Claim Boundaries

1. Validate as security hardening rather than a proven security fix.
2. Do not claim authentication bypass or signature forgery.
3. Do not claim confirmed remote DoS from the patch alone.
4. Treat the signature-length change as panic/input-validation hardening, separate from the zstd bomb claim.
