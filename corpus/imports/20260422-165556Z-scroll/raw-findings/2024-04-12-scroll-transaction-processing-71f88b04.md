---
case_id: case_20240412_71f88b04
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2024-04-12
source_refs:
  - git:71f88b04f5a69196138c8cec63a75cf1f0ba2d99
  - "common/types/encoding/codecv1/codecv1.go:335"
  - "common/types/encoding/codecv1/codecv1.go:228"
  - "common/types/encoding/codecv1/codecv1.go:303"
  - "common/types/encoding/codecv1/codecv1.go:275"
bug_class: cryptographic-binding
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - data-availability
  - cryptographic-binding
  - kzg4844
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes blob construction so it computes an EIP-4844 blob versioned hash, appends that hash to the challenge preimage, and returns it to callers. That is a real cryptographic-binding change in the DA encoding path. However, the supplied evidence does not show the downstream `piHash` use, verifier behavior, or any concrete acceptance flaw, so the material supports a security-relevant hardening/fix thesis only weakly and does not establish an actual vulnerability end to end.

## Observed Patch Facts

1. In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `return nil, nil, err` with `return nil, common.Hash{}, nil, err`.

2. In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `blob, z, err := constructBlobPayload(batch.Chunks)` with `blob, blobVersionedHash, z, err := constructBlobPayload(batch.Chunks)`.

3. In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `return nil, nil, err` with `return nil, common.Hash{}, nil, err`.

4. In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `func constructBlobPayload(chunks []*encoding.Chunk) (*kzg4844.Blob, *kzg4844.Point, e...` with `func constructBlobPayload(chunks []*encoding.Chunk) (*kzg4844.Blob, common.Hash, *kzg...`.

## Project Context

The changed code sits primarily in `common/types/encoding/codecv1`, `common/types/encoding`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `common/types/encoding/codecv1/codecv1_test.go`, `common/types/encoding/da.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `common/types/encoding/codecv1/codecv1_test.go`, `common/types/encoding/da.go`. The strongest project-level identifiers around this patch are `blob`, `kzg4844`, `constructBlobPayload`, and `common`.

## Before/After Behavior

Before the change, `constructBlobPayload` returned only the blob and challenge point, and the shown challenge-preimage construction covered metadata and per-chunk hashes. After the change, `constructBlobPayload` returns an additional `common.Hash`, computes a blob commitment and `blobVersionedHash`, and copies that hash into an added final slot in `challengePreimage`. `NewDABatch` now receives `blobVersionedHash` from blob construction instead of only receiving `blob` and `z`.

# Root Cause

The shown encoding path did not previously include the blob's versioned hash in the challenge transcript and did not expose that hash as part of the blob-construction API. That indicates incomplete binding of the transcript to the final blob commitment, but the provided evidence does not prove the full impact of that omission.

## Walkthrough

1. `constructBlobPayload` changes signature from `(*kzg4844.Blob, *kzg4844.Point, error)` to `(*kzg4844.Blob, common.Hash, *kzg4844.Point, error)`, making a blob hash an explicit output.

2. Inside that function, the comment and allocation for `challengePreimage` are expanded to include one more 32-byte hash slot.

3. After `makeBlobCanonical(blobBytes)`, the new code computes a KZG commitment with `kzg4844.BlobToCommitment(*blob)` and derives `blobVersionedHash` with `kzg4844.CalcBlobHashV1(...)`.

4. The line copying `blobVersionedHash` into `challengePreimage[(1+MaxNumChunks)*32:]` shows the challenge transcript is now bound to that hash.

5. `NewDABatch` changes from receiving `blob, z, err` to receiving `blob, blobVersionedHash, z, err`, so the new binding value is propagated to later code paths.

6. The changed error returns are mechanical fallout from the new return signature and are not independent security evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| common/types/encoding/codecv1/codecv1.go | 335 | Computes the blob versioned hash and adds it to the challenge preimage used for the proof/challenge construction. |
| common/types/encoding/codecv1/codecv1.go | 228 | Threads the blob versioned hash out of blob construction into DA batch assembly so downstream public-input hashing can include the blob binding. |
| common/types/encoding/codecv1/codecv1.go | 275 | Changes the blob-construction API so the blob hash becomes an explicit output of the DA encoding path rather than an omitted implicit value. |

## Code Snippets

## Snippet 1

Context: `common/types/encoding/codecv1/codecv1.go:335` (changes signature or replay validation logic)

Before
```go
blob, err := makeBlobCanonical(blobBytes)
	if err != nil {
		return nil, nil, err
	}

	// compute z = challenge_digest % BLS_MODULUS
	challengeDigest := crypto.Keccak256Hash(challengePreimage)
```
After
```go
blob, err := makeBlobCanonical(blobBytes)
	if err != nil {
		return nil, common.Hash{}, nil, err
	}

	// compute blob versioned hash
	c, err := kzg4844.BlobToCommitment(*blob)
	if err != nil {
```

## Snippet 2

Context: `common/types/encoding/codecv1/codecv1.go:228` (changes a sensitive control or state-update path)

Before
```go
// blob payload
	blob, z, err := constructBlobPayload(batch.Chunks)
	if err != nil {
		return nil, err
	}

	// blob versioned hash
```
After
```go
// blob payload
	blob, blobVersionedHash, z, err := constructBlobPayload(batch.Chunks)
	if err != nil {
		return nil, err
	}

	daBatch := DABatch{
```

## Snippet 3

Context: `common/types/encoding/codecv1/codecv1.go:303` (changes signature or replay validation logic)

Before
```go
rlpTxData, err := encoding.ConvertTxDataToRLPEncoding(tx)
					if err != nil {
						return nil, nil, err
					}
					blobBytes = append(blobBytes, rlpTxData...)
```
After
```go
rlpTxData, err := encoding.ConvertTxDataToRLPEncoding(tx)
					if err != nil {
						return nil, common.Hash{}, nil, err
					}
					blobBytes = append(blobBytes, rlpTxData...)
```

## Snippet 4

Context: `common/types/encoding/codecv1/codecv1.go:275` (changes signature or replay validation logic)

Before
```go
// constructBlobPayload constructs the 4844 blob payload.
func constructBlobPayload(chunks []*encoding.Chunk) (*kzg4844.Blob, *kzg4844.Point, error) {
	// metadata consists of num_chunks (2 bytes) and chunki_size (4 bytes per chunk)
	metadataLength := 2 + MaxNumChunks*4
```
After
```go
// constructBlobPayload constructs the 4844 blob payload.
func constructBlobPayload(chunks []*encoding.Chunk) (*kzg4844.Blob, common.Hash, *kzg4844.Point, error) {
	// metadata consists of num_chunks (2 bytes) and chunki_size (4 bytes per chunk)
	metadataLength := 2 + MaxNumChunks*4
```

# Fix Pattern

Add the missing commitment-derived value to a cryptographic transcript and propagate it through the API so later stages can consume the same bound value.

## How It Was Fixed

The fix canonicalizes the blob, computes its KZG commitment, derives the blob versioned hash, inserts that hash into the challenge preimage, and returns the hash from `constructBlobPayload` so callers can carry it forward. The evidence supports transcript strengthening; it does not directly show all downstream uses named in the commit subject.

# Why It Matters

1. The patch changes cryptographic binding logic rather than only refactoring return values.

2. Without the blob-derived hash in the shown preimage, the challenge is bound to less context than after the patch.

3. The affected code sits in DA batch encoding, so transcript composition is plausibly security relevant.

4. The provided snippets do not show a verifier bypass, forgery, or replay, so impact should not be overstated.

# Evidence Notes

Direct evidence supports only these points: the challenge preimage gained a blob-versioned-hash slot; the code now computes that hash from the blob commitment; and the value is returned to `NewDABatch`. The commit subject mentions adding `blobHash` to `piHash`, but no snippet in the supplied evidence shows that downstream hashing change. No verifier, contract acceptance path, exploit scenario, or regression test content is included, so stronger claims about concrete vulnerability impact are not established here. Protocol security invariant: The challenge material for a DA blob should be bound to the exact blob commitment/versioned hash, not only to metadata and per-chunk hashes. The provided evidence also suggests that downstream batch hashing may need the same binding, but that part is not shown directly. Verification notes: The patch does not by itself prove an attacker could forge a valid proof or bypass on-chain verification. The provided evidence does not include the full verifier or contract-side acceptance logic. It is not proven from this diff alone whether the issue enabled replay across different blobs or only a narrower integrity mismatch. The diff does not establish whether any historical batches or live deployments were affected. No direct evidence was provided for how `blobVersionedHash` is consumed after `NewDABatch`. No contract-side or verifier-side logic was shown. No test diff was provided to confirm the intended security property. This is best classified as security-relevant but not proven as a concrete vulnerability fix from the supplied material alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-binding`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, data-availability, cryptographic-binding, kzg4844`

The patch is in a security-sensitive cryptographic path and clearly strengthens binding between the generated challenge transcript and the actual EIP-4844 blob by computing the blob commitment-derived versioned hash and appending it to the preimage. That is stronger evidence than a generic correctness fix, so this belongs as security hardening. However, the supplied diff does not show the full verifier or `piHash` consumption path, and it does not prove a concrete exploitable acceptance bypass, so it should not be elevated to a confirmed security-fix for a specific vulnerability.

## Security Evidence

1. `constructBlobPayload` now returns a `blobVersionedHash` in addition to the blob and challenge point.
2. The challenge preimage is explicitly expanded to include an extra 32-byte slot for the blob versioned hash.
3. The code computes a KZG commitment from the canonical blob and derives `blobVersionedHash` from that commitment.
4. The patch copies `blobVersionedHash` into the challenge preimage, tightening transcript binding to the actual blob commitment.
5. `NewDABatch` is updated to receive and propagate the blob versioned hash, showing intentional end-to-end use of the new binding value.

## Missing Evidence

1. No supplied snippet shows the downstream `piHash` change named in the commit subject.
2. No verifier, contract acceptance, or proof-checking path is shown to demonstrate a concrete bypass before the patch.
3. No test excerpt is provided that states the intended security property or reproduces a failing attack scenario.
4. The diff does not show whether distinct blobs could previously share the same accepted challenge/public-input state in practice.

## Claim Boundaries

1. Supported claim: the patch hardens cryptographic binding in the DA/blob encoding path.
2. Supported claim: before the patch, the shown challenge preimage omitted the blob versioned hash.
3. Unsupported claim: the patch definitively fixes a proven exploitable vulnerability.
4. Unsupported claim: the exact impact was replay, forgery, or verifier bypass; the evidence does not establish which.
5. Unsupported claim: all downstream public-input hashing and verifier logic are covered by the supplied patch evidence.
