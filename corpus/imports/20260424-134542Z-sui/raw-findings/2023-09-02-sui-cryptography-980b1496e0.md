---
case_id: case_20230902_980b1496e0
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2023-09-02
source_refs:
  - git:980b1496e01b4e1bf1934ebd378c8bd77f504faf
  - "sdk/typescript/src/multisig/publickey.ts:196"
  - "sdk/typescript/src/multisig/publickey.ts:84"
  - "sdk/typescript/src/multisig/publickey.ts:109"
  - "sdk/typescript/src/multisig/publickey.ts:226"
bug_class: multisig-input-validation
impact_type:
  - sdk-cryptographic-integrity-hardening
tags:
  - infrastructure
  - cryptography
  - multisig
  - signature
  - input-validation
  - sdk-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens TypeScript SDK multisig handling by adding validation around `MultiSigPublicKey` construction and partial-signature combination. The evidence supports a security-relevant SDK multisig parameter-validation issue, but does not prove a consensus-layer vulnerability, full-node acceptance issue, transaction forgery, or fund-loss exploit.

## Observed Patch Facts

1. In `sdk/typescript/src/multisig/publickey.ts`, the patch replaces `async verify(` with `async verify(message: Uint8Array, multisigSignature: SerializedSignature): Promise<bo...`.

2. In `sdk/typescript/src/multisig/publickey.ts`, the patch replaces `this.publicKeys = this.multisigPublicKey.pk_map.map(({ pubKey, weight }) => {` with `if (this.multisigPublicKey.threshold < 1) {`.

3. In `sdk/typescript/src/multisig/publickey.ts`, the patch replaces `if (this.publicKeys.length > MAX_SIGNER_IN_MULTISIG) {` with `const totalWeight = this.publicKeys.reduce((sum, { weight }) => sum + weight, 0);`.

4. In `sdk/typescript/src/multisig/publickey.ts`, the patch replaces `let bitmap = 0;` with `/**`.

## Project Context

The changed code sits primarily in `sdk/typescript/src/multisig`, `sdk/typescript/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `sdk/typescript/src/multisig/index.ts`, `sdk/typescript/src/cryptography/multisig.ts` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/typescript/src/cryptography/multisig.ts`, `sdk/typescript/src/verify/index.ts`. The strongest project-level identifiers around this patch are `throw`, `Error`, `threshold`, and `Uint8Array`. Nearby tests or test-like files include `sdk/typescript/src/builder/__tests__/Transaction.test.ts`, `sdk/typescript/src/builder/__tests__/bcs.test.ts`.

## Before/After Behavior

Before the patch, the shown constructor path mapped multisig public keys and weights without the added checks for `threshold < 1`, duplicate public keys, or `threshold > totalWeight`. After the patch, those invalid configurations are rejected. The constructor also adds a minimum signer count check, and `combinePartialSignatures` rejects too many partial signatures before building bitmap/compressed signature data. The `verify` method type is narrowed to `SerializedSignature`, which is API tightening rather than strong standalone vulnerability evidence.

# Root Cause

The grounded root cause is incomplete SDK-side validation of multisig public key and signature-bundle parameters at construction and combination boundaries. Stronger claims about on-chain authorization bypass or replay are not supported by the provided evidence.

## Walkthrough

1. `MultiSigPublicKey` can be built from serialized bytes, raw bytes, or a structured multisig public key value.

2. The patch rejects `this.multisigPublicKey.threshold < 1` during construction.

3. The patch tracks configured public keys and rejects duplicates.

4. The patch sums configured signer weights and rejects a threshold greater than total weight.

5. The patch adds a minimum signer count check alongside existing signer count bounds.

6. `combinePartialSignatures` now rejects signature arrays longer than `MAX_SIGNER_IN_MULTISIG` before bitmap/compressed-signature construction.

7. `verify` is narrowed to serialized signatures and continues parsing and scheme validation for `MultiSig`, but this type-level cleanup is not enough by itself to establish a vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/typescript/src/multisig/publickey.ts | 84 | validates multisig public key threshold and rejects duplicate public keys during construction/deserialization |
| sdk/typescript/src/multisig/publickey.ts | 109 | checks aggregate signer weight can satisfy the configured threshold and enforces signer count bounds |
| sdk/typescript/src/multisig/publickey.ts | 196 | verifies serialized multisig signatures and enforces MultiSig signature scheme parsing |
| sdk/typescript/src/multisig/publickey.ts | 226 | combines partial signatures while bounding the number of submitted signatures |

## Code Snippets

## Snippet 1

Context: `sdk/typescript/src/multisig/publickey.ts:196` (changes an authorization or privilege gate)

Before
```ts
* Verifies that the signature is valid for for the provided message
	 */
	async verify(
		message: Uint8Array,
		multisigSignature: Uint8Array | SerializedSignature,
	): Promise<boolean> {
		if (typeof multisigSignature !== 'string') {
			throw new Error('Multisig verification only supports serialized signature');
```
After
```ts
* Verifies that the signature is valid for for the provided message
	 */
	async verify(message: Uint8Array, multisigSignature: SerializedSignature): Promise<boolean> {
		// Multisig verification only supports serialized signature
		const { signatureScheme, multisig } = parseSerializedSignature(multisigSignature);
```

## Snippet 2

Context: `sdk/typescript/src/multisig/publickey.ts:84` (changes an authorization or privilege gate)

Before
```ts
this.rawBytes = builder.ser('MultiSigPublicKey', value).toBytes();
		}

		this.publicKeys = this.multisigPublicKey.pk_map.map(({ pubKey, weight }) => {
			const [scheme, bytes] = Object.entries(pubKey)[0] as [SignatureScheme, number[]];
			return {
				publicKey: publicKeyFromRawBytes(scheme, Uint8Array.from(bytes)),
```
After
```ts
this.rawBytes = builder.ser('MultiSigPublicKey', value).toBytes();
		}
		if (this.multisigPublicKey.threshold < 1) {
			throw new Error('Invalid threshold');
		}

		const seenPublicKeys = new Set<string>();
```

## Snippet 3

Context: `sdk/typescript/src/multisig/publickey.ts:109` (changes an authorization or privilege gate)

Before
```ts
});

		if (this.publicKeys.length > MAX_SIGNER_IN_MULTISIG) {
			throw new Error(`Max number of signers in a multisig is ${MAX_SIGNER_IN_MULTISIG}`);
		}
	}

	static fromPublicKeys({
```
After
```ts
});

		const totalWeight = this.publicKeys.reduce((sum, { weight }) => sum + weight, 0);

		if (this.multisigPublicKey.threshold > totalWeight) {
			throw new Error(`Unreachable threshold`);
		}
```

## Snippet 4

Context: `sdk/typescript/src/multisig/publickey.ts:226` (changes a sensitive control or state-update path)

Before
```ts
}

	combinePartialSignatures(signatures: SerializedSignature[]): SerializedSignature {
		let bitmap = 0;
		const compressedSignatures: CompressedSignature[] = new Array(signatures.length);
```
After
```ts
}

	/**
	 * Combines multiple partial signatures into a single multisig, ensuring that each public key signs only once
	 * and that all the public keys involved are known and valid, and then serializes multisig into the standard format
	 */
	combinePartialSignatures(signatures: SerializedSignature[]): SerializedSignature {
		if (signatures.length > MAX_SIGNER_IN_MULTISIG) {
```

# Fix Pattern

Add explicit validation at SDK construction and signature-combination boundaries for multisig threshold validity, signer uniqueness, reachable aggregate weight, signer count bounds, and partial signature count bounds.

## How It Was Fixed

The patch added constructor guards for invalid thresholds, duplicate public keys, unreachable thresholds, and too few signers. It also added a `combinePartialSignatures` input-length guard and tightened the `verify` method signature to accept serialized signatures directly.

# Why It Matters

1. Preserves SDK-side multisig threshold semantics.

2. Prevents duplicate configured public keys from distorting signer accounting in SDK-created multisig artifacts.

3. Rejects unreachable or nonsensical multisig configurations early.

4. Bounds partial-signature input before serialization work proceeds.

5. Does not establish a validator or consensus-layer vulnerability from the provided evidence.

# Evidence Notes

The strongest evidence is in `sdk/typescript/src/multisig/publickey.ts` around the added threshold, duplicate public key, total weight, signer count, and partial signature count checks. The commit message references audit findings, including Medium and Low issues, which supports security relevance. However, the provided evidence does not include the audit report details, an exploit scenario, or proof that malformed SDK multisig artifacts would be accepted by full nodes. Claims about replay, transaction forgery, fund theft, or protocol-level behavior should be removed. Protocol security invariant: SDK-created or SDK-verified multisig artifacts should preserve threshold semantics: thresholds should be positive and reachable by configured signer weights, public keys should not be duplicated in a way that can distort signer accounting, and combined signature inputs should be bounded before serialization or verification work proceeds. Verification notes: No on-chain validator or consensus-layer behavior change is shown. The patch does not by itself prove transaction forgery or fund theft was exploitable. The evidence does not show whether invalid SDK-created multisig objects would be accepted by full nodes. The verify method type change alone looks like API tightening, not a standalone vulnerability fix. The specific audit issue labels are named but their detailed findings are not provided. Supported: SDK-side multisig parameter validation was added. Supported: duplicate public keys and unreachable thresholds are now rejected. Supported: excessive partial signatures are now rejected before combination. Not supported: consensus-layer or validator behavior changed. Not supported: a demonstrated transaction forgery or fund-loss exploit. Not supported: replay vulnerability classification. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `multisig-input-validation`
Final impact type: `sdk-cryptographic-integrity-hardening`
Final tags: `infrastructure, cryptography, multisig, signature, input-validation, sdk-hardening`

The supplied evidence supports retaining this as security hardening, not a proven concrete security fix. The commit explicitly references a security audit and changes TypeScript SDK multisig/cryptography code to reject invalid thresholds, duplicate public keys, unreachable thresholds, too few or too many signers, and excessive partial signatures. These are security-sensitive validation improvements around signature and multisig semantics. However, the patch evidence does not prove replay, request forgery, validator acceptance, consensus impact, fund loss, or an exploitable authorization bypass.

## Security Evidence

1. Commit subject and body explicitly tie the patch to a security audit and named audit findings.
2. Multisig public key construction now rejects threshold values below 1.
3. Constructor now rejects duplicate public keys in a multisig key map.
4. Constructor now rejects thresholds greater than total signer weight and too few signers.
5. Partial signature combination now bounds the number of supplied signatures before processing.
6. The affected code is in SDK cryptography/multisig signature handling paths.

## Missing Evidence

1. No audit report details are provided for Medium-1 or Low-1.
2. No exploit scenario or proof of transaction forgery is shown.
3. No evidence shows malformed SDK multisig artifacts would be accepted by validators or full nodes.
4. No consensus-layer, node-side, or on-chain authorization change is shown.
5. No direct evidence supports a replay-specific classification.

## Claim Boundaries

1. Keep the finding scoped to SDK-side multisig validation hardening.
2. Do not claim a proven request-forgery, replay, fund-loss, or consensus vulnerability.
3. The verify signature type narrowing is API tightening and not strong standalone vulnerability evidence.
4. The evidence supports security relevance because invalid cryptographic multisig states are rejected earlier, not because a concrete exploit is demonstrated.
