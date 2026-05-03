---
case_id: case_20250115_c008e2912
project: movement
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: medium
source_quality: high
date: 2025-01-15
source_refs:
  - git:c008e2912c83cfdecfbe359b7ac603a8dc2759f0
  - "protocol-units/da/movement/protocol/light-node/src/passthrough.rs:134"
  - "protocol-units/da/movement/protocol/light-node/src/passthrough.rs:39"
  - "protocol-units/da/movement/protocol/light-node/src/sequencer.rs:52"
  - "protocol-units/da/movement/protocol/light-node/src/manager.rs:48"
bug_class: missing-signature-verification
impact_type:
  - client-data-integrity
tags:
  - blockchain-core
  - rpc-client-api
  - da-light-node
  - signature-verification
  - authenticity-check
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit c008e2912 restores verifier-gated handling in the DA light-node pass-through read stream. Before the patch, stream_read_from_height converted each DaBlob from the DA stream directly into a pass-through RPC response. After the patch, it calls verifier.verify(da_blob, height.as_u64()).await first and only serializes the verified inner blob. The surrounding type changes wire a VerifierOperations implementation, specifically InKnownSignersVerifier in the shown construction path, into the light-node types.

## Observed Patch Facts

1. In `protocol-units/da/movement/protocol/light-node/src/passthrough.rs`, the patch replaces `let blob = da_blob.to_blob_passed_through_read_response(height.as_u64()).map_err(|e|...` with `let verifed_blob = verifier.verify(da_blob, height.as_u64()).await.map_err(|e| tonic:...`.

2. In `protocol-units/da/movement/protocol/light-node/src/passthrough.rs`, the patch replaces `// pub verifier: Arc<Box<dyn VerifierOperations<CelestiaBlob, DaBlob> + Send + Sync>>,` with `V: VerifierOperations<DaBlob, DaBlob>,`.

3. In `protocol-units/da/movement/protocol/light-node/src/sequencer.rs`, the patch replaces `pub pass_through: LightNodePassThrough<C, Da>,` with `V: VerifierOperations<DaBlob, DaBlob>,`.

4. In `protocol-units/da/movement/protocol/light-node/src/manager.rs`, the patch replaces `) -> Result<LightNode<C, DigestStoreDa<CelestiaDa>>, anyhow::Error>` with `) -> Result<LightNode<C, DigestStoreDa<CelestiaDa>, InKnownSignersVerifier<C>>, anyho...`.

## Project Context

The changed code sits primarily in `protocol-units/da/movement/protocol/light-node/src`, `protocol-units/da/movement/protocol/light-node`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `protocol-units/da/movement/protocol/light-node/src/light_node.rs`, `protocol-units/da/movement/protocol/light-node/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/da/movement/protocol/light-node/src/light_node.rs`. The strongest project-level identifiers around this patch are `tonic::Status::internal`, `blob`, `anyhow::Error`, and `DaBlob`.

## Before/After Behavior

Before the patch, the pass-through stream read path took each (height, da_blob) from da.stream_ir_blobs_from_height and directly called to_blob_passed_through_read_response. After the patch, the path clones self.verifier, verifies each da_blob with its height, and converts only the verified inner blob into the RPC response. The LightNode and sequencer wrapper types were updated to carry a verifier generic, and manager/runtime construction now uses InKnownSignersVerifier.

# Root Cause

The pass-through RPC read path did not apply the configured verifier before serializing DA blobs for clients. The evidence supports a missing validation issue in this specific read path, but it does not establish the full attacker model, how the trusted signer set is defined, or whether arbitrary untrusted DA blobs could be injected upstream.

## Walkthrough

1. A client calls the light-node stream_read_from_height RPC path.

2. The service obtains a DA blob stream with da.stream_ir_blobs_from_height(height).

3. Before the patch, each returned da_blob was directly converted into a pass-through read response.

4. The patch adds a verifier field to the pass-through light node and propagates the verifier-aware type through sequencer and manager construction.

5. The patched stream calls verifier.verify(da_blob, height.as_u64()).await for each blob.

6. Only the verified blob's inner value is converted into StreamReadFromHeightResponse.

7. Verifier errors prevent normal response construction for that blob by returning a tonic internal status.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/da/movement/protocol/light-node/src/passthrough.rs | 120 | RPC stream_read_from_height reads DA blobs and now verifies each blob at its height before returning it to clients. |
| protocol-units/da/movement/protocol/light-node/src/passthrough.rs | 33 | LightNode pass-through type now carries a verifier implementing VerifierOperations<DaBlob, DaBlob>. |
| protocol-units/da/movement/protocol/light-node/src/sequencer.rs | 46 | Sequencer light-node wrapper propagates the verifier-aware pass-through type. |
| protocol-units/da/movement/protocol/light-node/src/manager.rs | 48 | Manager construction returns a light node parameterized with InKnownSignersVerifier. |
| protocol-units/da/movement/protocol/light-node/src/main.rs | 12 | Runtime type instantiation uses InKnownSignersVerifier for the light node. |

## Code Snippets

## Snippet 1

Context: `protocol-units/da/movement/protocol/light-node/src/passthrough.rs:134` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
while let Some(blob) = blob_stream.next().await {
				let (height, da_blob) = blob.map_err(|e| tonic::Status::internal(e.to_string()))?;
				let blob = da_blob.to_blob_passed_through_read_response(height.as_u64()).map_err(|e| tonic::Status::internal(e.to_string()))?;
				let response = StreamReadFromHeightResponse {
					blob: Some(blob)
```
After
```rust
while let Some(blob) = blob_stream.next().await {
				let (height, da_blob) = blob.map_err(|e| tonic::Status::internal(e.to_string()))?;
				let verifed_blob = verifier.verify(da_blob, height.as_u64()).await.map_err(|e| tonic::Status::internal(e.to_string()))?;
				let blob = verifed_blob.into_inner().to_blob_passed_through_read_response(height.as_u64()).map_err(|e| tonic::Status::internal(e.to_string()))?;
				let response = StreamReadFromHeightResponse {
					blob: Some(blob)
```

## Snippet 2

Context: `protocol-units/da/movement/protocol/light-node/src/passthrough.rs:39` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
FieldBytesSize<C>: ModulusSize,
	Da: DaOperations,
{
	pub config: Config,
	// pub verifier: Arc<Box<dyn VerifierOperations<CelestiaBlob, DaBlob> + Send + Sync>>,
	pub signing_key: SigningKey<C>,
	pub da: Arc<Da>,
}
```
After
```rust
FieldBytesSize<C>: ModulusSize,
	Da: DaOperations,
	V: VerifierOperations<DaBlob, DaBlob>,
{
	pub config: Config,
	pub signing_key: SigningKey<C>,
	pub da: Arc<Da>,
	pub verifier: Arc<V>,
```

## Snippet 3

Context: `protocol-units/da/movement/protocol/light-node/src/sequencer.rs:52` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
FieldBytesSize<C>: ModulusSize,
	Da: DaOperations,
{
	pub pass_through: LightNodePassThrough<C, Da>,
	pub memseq: Arc<memseq::Memseq<memseq::RocksdbMempool>>,
	pub prevalidator: Option<Arc<Validator>>,
}
```
After
```rust
FieldBytesSize<C>: ModulusSize,
	Da: DaOperations,
	V: VerifierOperations<DaBlob, DaBlob>,
{
	pub pass_through: LightNodePassThrough<C, Da, V>,
	pub memseq: Arc<memseq::Memseq<memseq::RocksdbMempool>>,
	pub prevalidator: Option<Arc<Validator>>,
}
```

## Snippet 4

Context: `protocol-units/da/movement/protocol/light-node/src/manager.rs:48` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
pub async fn try_light_node(
		&self,
	) -> Result<LightNode<C, DigestStoreDa<CelestiaDa>>, anyhow::Error>
	where
		C: PrimeCurve + CurveArithmetic + DigestPrimitive + PointCompression,
```
After
```rust
pub async fn try_light_node(
		&self,
	) -> Result<LightNode<C, DigestStoreDa<CelestiaDa>, InKnownSignersVerifier<C>>, anyhow::Error>
	where
		C: PrimeCurve + CurveArithmetic + DigestPrimitive + PointCompression,
```

# Fix Pattern

Inject the configured verifier into the pass-through read path and make RPC response construction depend on successful per-blob verification.

## How It Was Fixed

The fix made the pass-through LightNode generic over V: VerifierOperations<DaBlob, DaBlob>, added pub verifier: Arc<V>, propagated that generic through the sequencer wrapper, and changed manager/runtime construction to use InKnownSignersVerifier. stream_read_from_height now verifies each blob at its associated height before converting it to the RPC response type.

# Why It Matters

1. Prevents the shown RPC path from serving DA blobs before the configured verifier runs.

2. Restores an authenticity or signer-related validation step implied by InKnownSignersVerifier.

3. Limits the finding to the pass-through read stream; broader ingestion or sequencing behavior is not proven by the supplied evidence.

4. The evidence does not prove arbitrary attacker injection or concrete downstream client impact.

# Evidence Notes

The strongest evidence is the changed loop in protocol-units/da/movement/protocol/light-node/src/passthrough.rs around stream_read_from_height, where direct conversion of da_blob was replaced by verifier.verify(da_blob, height.as_u64()).await followed by conversion of verifed_blob.into_inner(). Supporting evidence is the addition of V: VerifierOperations<DaBlob, DaBlob>, pub verifier: Arc<V>, propagation through sequencer.rs, and manager/main use of InKnownSignersVerifier. Unsupported claims about replay acceptance, attacker-controlled blob injection, trusted signer-set contents, or concrete client compromise should not be made from this input alone. Protocol security invariant: DA blobs served through the light-node pass-through read stream should pass the configured VerifierOperations<DaBlob, DaBlob> check before being emitted to RPC clients. The supplied evidence shows the verifier receives both the blob and its height before response construction. Verification notes: The patch does not show how InKnownSignersVerifier defines the trusted signer set. The patch does not prove that untrusted attackers could inject arbitrary DA blobs into the underlying DA stream. The patch does not prove replay acceptance beyond the fact that verification is height-sensitive. The patch does not show client-side consequences of receiving an unverified blob. The patch is limited to the light-node pass-through read path shown, not all DA ingestion or sequencing paths. Confirmed from supplied diff snippets that the stream path now calls verifier.verify before response serialization. Confirmed from supplied snippets that verifier plumbing was added to pass-through and sequencer types. Confirmed from supplied snippets that manager/runtime construction references InKnownSignersVerifier. No tests or exploit reproduction were provided. Attacker model and downstream impact remain unproven. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signature-verification`
Final impact type: `client-data-integrity`
Final tags: `blockchain-core, rpc-client-api, da-light-node, signature-verification, authenticity-check`

The supplied patch clearly reintegrates a verifier into a DA light-node pass-through read stream before blobs are serialized and returned to RPC clients, and wires an InKnownSignersVerifier into the relevant construction path. That is security-sensitive authenticity enforcement and supports keeping the case as security hardening. The evidence does not prove a concrete exploitable vulnerability, arbitrary attacker injection, replay behavior, or downstream client compromise, so security-fix and the original state-divergence framing are too strong.

## Security Evidence

1. stream_read_from_height changed from directly serializing da_blob to calling verifier.verify(da_blob, height.as_u64()).await first
2. the verified inner blob is the value converted into the pass-through read response
3. LightNodePassThrough now stores a verifier implementing VerifierOperations<DaBlob, DaBlob>
4. manager/runtime construction references InKnownSignersVerifier for the light node

## Missing Evidence

1. no attacker model showing untrusted parties can inject arbitrary DA blobs into the stream
2. no details showing how InKnownSignersVerifier defines or enforces the trusted signer set
3. no exploit, test, or failure case demonstrating prior client compromise or consensus impact
4. no proof of replay acceptance beyond the verifier receiving a height parameter

## Claim Boundaries

1. valid only for the light-node pass-through read stream shown in the evidence
2. supports authenticity/signature verification hardening, not a proven end-to-end exploit fix
3. does not establish broader DA ingestion, sequencing, or consensus behavior
4. does not justify specific claims of state-consistency failure or client-view divergence from the patch alone
