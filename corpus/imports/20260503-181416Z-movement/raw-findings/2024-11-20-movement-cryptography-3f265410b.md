---
case_id: case_20241120_3f265410b
project: movement
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-11-20
source_refs:
  - git:3f265410b13502ac3ec43009802f900330472754
  - "protocol-units/da/m1/util/src/ir_blob.rs:86"
  - "protocol-units/da/m1/util/src/ir_blob.rs:161"
  - "protocol-units/da/m1/util/src/ir_blob.rs:64"
  - "protocol-units/da/m1/util/src/ir_blob.rs:25"
bug_class: signed-field-not-bound
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - signature
  - signed-data-binding
  - integrity-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes M1 DA signed blob signing and verification so the wrapper `id` is included in the digest being signed and verified. Before, the observed wrapper verification delegated to `self.data.try_verify(...)`, which did not include the wrapper-level `id` in the shown call path. After, verification hashes `self.data.blob`, `self.data.timestamp`, and `self.id` before checking the ECDSA signature. This is plausibly security-relevant cryptographic binding work, but the provided evidence does not prove downstream impact or exploitability, so it should not be treated as a confirmed security fix.

## Observed Patch Facts

1. In `protocol-units/da/m1/util/src/ir_blob.rs`, the patch replaces `self.data.try_verify::<C>(self.signature.as_slice(), self.signer.as_slice())` with `let mut hasher = C::Digest::new();`.

2. In `protocol-units/da/m1/util/src/ir_blob.rs`, the patch replaces `pub mod celestia {` with `#[cfg(test)]`.

3. In `protocol-units/da/m1/util/src/ir_blob.rs`, the patch replaces `id: prehash_bytes.to_vec(),` with `id,`.

4. In `protocol-units/da/m1/util/src/ir_blob.rs`, the patch replaces `pub fn try_to_sign<C>(` with `pub fn compute_id<C>(&self) -> Vec<u8>`.

## Project Context

The changed code sits primarily in `protocol-units/da/m1/util/src`, `protocol-units/da/m1/util`, which anchors the finding in the `cryptography` area of the project. Historical context from `protocol-units/da/m1/util/src/lib.rs`, `protocol-units/da/m1/util/src/config/local/m1_da_light_node.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/da/m1/util/src/config/local/m1_da_light_node.rs`, `protocol-units/da/m1/util/src/config/mod.rs`. The strongest project-level identifiers around this patch are `C::Digest::new`, `signature`, `as_slice`, and `hasher`.

## Before/After Behavior

Before the patch, `InnerSignedBlobV1::try_verify` delegated verification to the inner data object using the signature and signer, and the supplied evidence does not show the wrapper `id` being included in that verification path. The signing path stored `id: prehash_bytes.to_vec()`. After the patch, `compute_id` derives an id from blob bytes and timestamp, signing stores that computed id, and both signing and verification hash blob bytes, timestamp, and id. A regression test was added for changing the id after signing and expecting verification to fail.

# Root Cause

The observed issue was a mismatch between the signed wrapper fields and the verification digest: the wrapper carried an `id`, but the pre-patch verification path shown in the evidence did not bind that wrapper field. The evidence supports an integrity-binding gap, but not a proven protocol-level vulnerability.

## Walkthrough

1. `InnerSignedBlobV1Data::compute_id` was added to hash blob bytes and timestamp into a canonical id value.

2. `try_to_sign` now stores the computed id instead of storing `prehash_bytes` directly.

3. `try_to_sign` now builds the signed digest from blob bytes, timestamp bytes, and `id.as_slice()`.

4. `InnerSignedBlobV1::try_verify` no longer delegates to the inner data verifier; it reconstructs a digest using the wrapper's blob, timestamp, and id.

5. The verifier parses the public key and signature, then returns an error when `verify_digest` fails.

6. The added test documents that changing `id` on an already signed blob should invalidate verification.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/da/m1/util/src/ir_blob.rs | 25 | computes canonical blob id from blob bytes and timestamp |
| protocol-units/da/m1/util/src/ir_blob.rs | 41 | signing path now signs blob bytes, timestamp, and computed id |
| protocol-units/da/m1/util/src/ir_blob.rs | 80 | verification path now verifies the signature against blob bytes, timestamp, and stored id |
| protocol-units/da/m1/util/src/ir_blob.rs | 149 | public intermediate representation signature verification dispatch |
| protocol-units/da/m1/util/src/ir_blob.rs | 161 | regression test that changing id invalidates verification |

## Code Snippets

## Snippet 1

Context: `protocol-units/da/m1/util/src/ir_blob.rs:86` (changes signature or replay validation logic)

Before
```rust
FieldBytesSize<C>: ModulusSize,
	{
		self.data.try_verify::<C>(self.signature.as_slice(), self.signer.as_slice())
	}
}
```
After
```rust
FieldBytesSize<C>: ModulusSize,
	{
		let mut hasher = C::Digest::new();
		hasher.update(self.data.blob.as_slice());
		hasher.update(&self.data.timestamp.to_be_bytes());
		hasher.update(self.id.as_slice());

		let verifying_key = VerifyingKey::<C>::from_sec1_bytes(self.signer.as_slice())?;
```

## Snippet 2

Context: `protocol-units/da/m1/util/src/ir_blob.rs:161` (changes signature or replay validation logic)

Before
```rust
}

pub mod celestia {
```
After
```rust
}

#[cfg(test)]
pub mod test {

	use super::*;

	#[test]
```

## Snippet 3

Context: `protocol-units/da/m1/util/src/ir_blob.rs:64` (changes signature or replay validation logic)

Before
```rust
signature: signature.to_vec(),
			signer: signing_key.verifying_key().to_sec1_bytes().to_vec(),
			id: prehash_bytes.to_vec(),
		})
	}

	pub fn try_verify<C>(&self, signature: &[u8], signer: &[u8]) -> Result<(), anyhow::Error>
	where
```
After
```rust
signature: signature.to_vec(),
			signer: signing_key.verifying_key().to_sec1_bytes().to_vec(),
			id,
		})
	}
}
```

## Snippet 4

Context: `protocol-units/da/m1/util/src/ir_blob.rs:25` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

	pub fn try_to_sign<C>(
		self,
```
After
```rust
}

	pub fn compute_id<C>(&self) -> Vec<u8>
	where
		C: PrimeCurve + CurveArithmetic + DigestPrimitive + PointCompression,
		Scalar<C>: Invert<Output = CtOption<Scalar<C>>> + SignPrimitive<C>,
		SignatureSize<C>: ArrayLength<u8>,
		AffinePoint<C>: FromEncodedPoint<C> + ToEncodedPoint<C> + VerifyPrimitive<C>,
```

# Fix Pattern

Include the wrapper-level integrity-relevant field in the signed and verified digest, and add a regression test for post-signing mutation of that field.

## How It Was Fixed

The patch added `compute_id`, changed signing to include the computed id in the signed digest, changed verification to include the stored wrapper id in the verified digest, and added a test that mutating the id causes verification failure.

# Why It Matters

1. Pre-patch evidence suggests the wrapper `id` could be changed without affecting the observed signature check.

2. Binding `id` in the signature makes post-signing id mutation detectable.

3. The evidence does not show how a forged or changed id affects DA, consensus, authorization, or funds.

# Evidence Notes

Primary evidence is limited to `protocol-units/da/m1/util/src/ir_blob.rs`. The denial-of-service, panic, malformed-input, consensus, and validator-impact claims from the heuristic baseline are unsupported. The mapper's stronger `confirmed` verdict is also too strong because the supplied evidence does not show downstream reliance on `id` or a concrete exploit path. The patch is best classified as plausible cryptographic integrity hardening with unclear vulnerability status. Protocol security invariant: A signed blob representation should not allow fields that callers may treat as authenticated, such as the wrapper `id`, to be changed without invalidating signature verification. The supplied evidence shows the patch makes signature verification include `self.id`, but does not establish how that id is consumed downstream or whether accepting a changed id created an exploitable security violation. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show how downstream consensus or DA logic consumes a forged id. The patch does not prove key compromise or signer impersonation. The patch does not show a denial-of-service panic or malformed-input crash despite the heuristic baseline suggesting one. The verifier still appears to validate that the signature covers the supplied id, not independently prove from this evidence that the supplied id equals a recomputed id unless it was produced by the signing path. No external files or commands were inspected. Regression test name supports the intended behavior: changed id should not verify. Downstream use of `id` was not established by the supplied evidence. Verifier binds the supplied id; the evidence does not show verification independently recomputing and comparing the canonical id. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signed-field-not-bound`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, signature, signed-data-binding, integrity-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed exploit fix. Verification previously delegated to a data-only verifier while the wrapper carried an `id`; the patch signs and verifies a digest that includes blob bytes, timestamp, and `id`, and adds a regression test showing that changing `id` after signing must fail verification. That is a clear tightening of cryptographic integrity binding, but the evidence does not prove downstream exploitability, consensus impact, or liveness impact.

## Security Evidence

1. Verification now includes `self.id.as_slice()` in the digest checked by ECDSA verification.
2. Signing now computes an `id` and includes it in the signed digest.
3. A regression test was added for mutating the signed blob id and expecting verification failure.
4. The changed code is in a DA signed blob representation and touches signature verification behavior.

## Missing Evidence

1. No downstream code evidence shows how `id` is consumed for consensus, DA acceptance, authorization, or funds movement.
2. No proof is supplied that a mutable id was remotely exploitable before the patch.
3. No evidence supports the original liveness-failure impact classification.
4. No evidence shows verifier recomputes and compares a canonical id independently during verification.

## Claim Boundaries

1. Classify as cryptographic integrity hardening rather than a confirmed vulnerability fix.
2. Do not claim denial of service, liveness failure, fund loss, validator compromise, or consensus failure from the supplied patch alone.
3. The supported claim is limited to binding the wrapper `id` into the signed and verified data.
4. The patch proves intended behavior for id mutation rejection, not broader protocol impact.
