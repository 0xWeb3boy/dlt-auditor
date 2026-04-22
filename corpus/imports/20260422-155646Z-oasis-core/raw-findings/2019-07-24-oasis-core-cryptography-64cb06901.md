---
case_id: case_20190724_64cb06901
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: medium
date: 2019-07-24
source_refs:
  - git:64cb06901b6e8c357553537d6aef905a1750debd
  - "go/roothash/api/commitment/pool.go:151"
  - "go/roothash/api/commitment/pool.go:32"
  - "go/worker/compute/committee/node.go:236"
  - "go/worker/compute/committee/node.go:662"
bug_class: missing-signer-authorization
impact_type:
  - unauthorized-consensus-message-acceptance
tags:
  - consensus
  - signature-validation
  - committee-membership
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a specific authorization gap in roothash compute-commitment validation. Before the change, `TxnSchedSig` was checked with `VerifyTxnSchedSignature(blk.Header)`, and the code itself noted that it did not verify the signer was actually a transaction scheduler. After the change, the code requires `VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, ...)`, binding acceptance to committee-role membership.

## Observed Patch Facts

1. In `go/roothash/api/commitment/pool.go`, the patch replaces `// TODO: Also verify that the signature actually comes from a transaction` with `if err := sv.VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, []signatur...`.

2. In `go/roothash/api/commitment/pool.go`, the patch replaces `// StorageVerifier is an interface for verifying storage receipt signatures.` with `// SignatureVerifier is an interface for verifying storage and transaction`.

3. In `go/worker/compute/committee/node.go`, the patch replaces `if err := epoch.VerifyStorageCommittee(storageSignatures); err != nil {` with `if err := epoch.VerifyCommitteeSignatures(scheduler.KindStorage, storageSignatures);...`.

4. In `go/worker/compute/committee/node.go`, the patch replaces `if err := epoch.VerifyStorageCommittee(signatures); err != nil {` with `if err := epoch.VerifyCommitteeSignatures(scheduler.KindStorage, signatures); err !=...`.

## Project Context

The changed code sits primarily in `go/roothash/api/commitment`, `go/roothash/api`, `go/worker/compute/committee`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/roothash/api/commitment/txnscheduler.go`, `go/roothash/api/commitment/pool_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/roothash/api/commitment/pool_test.go`, `go/worker/compute/committee/state.go`. The strongest project-level identifiers around this patch are `signatures`, `scheduler`, `signature`, and `VerifyCommitteeSignatures`. Nearby tests or test-like files include `go/worker/compute/tests/tester.go`.

## Before/After Behavior

Before the patch, `addOpenComputeCommitment` accepted a transaction-scheduler signature based on `body.VerifyTxnSchedSignature(blk.Header)`, while a nearby TODO explicitly stated that the code still did not verify the signature came from a transaction scheduler. After the patch, the same path calls `sv.VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, []signature.Signature{body.TxnSchedSig})` and rejects the commitment if the signer is not authorized for that committee role. The storage-signature call-site changes in `node.go` support the same generalized verifier API, but the provided evidence most directly establishes the transaction-scheduler check as the primary fixed flaw.

# Root Cause

Compute-commitment admission validated the transaction-scheduler signature's cryptographic correctness but did not verify that the signer belonged to the active transaction scheduler committee.

## Walkthrough

1. In `go/roothash/api/commitment/pool.go`, the old code verified `TxnSchedSig` with `body.VerifyTxnSchedSignature(blk.Header)`.

2. That block contained an explicit TODO saying the code still needed to verify that the signature actually came from a transaction scheduler.

3. The patch replaces that check with `sv.VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, []signature.Signature{body.TxnSchedSig})`.

4. That change makes committee-role membership part of the acceptance decision for compute commitments.

5. The verifier abstraction in `pool.go` is widened to `VerifyCommitteeSignatures(kind, sigs)`, which matches the new role-aware validation model.

6. Updates in `go/worker/compute/committee/node.go` switch storage checks to the same generalized verifier, but those edits mainly show API consolidation around committee-kind-aware verification.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/roothash/api/commitment/pool.go | 151 | Admission check for open compute commitments; now enforces that `TxnSchedSig` is from the active transaction scheduler committee member. |
| go/roothash/api/commitment/pool.go | 32 | Verifier interface widened from storage-only checks to committee-kind-aware signature authorization. |
| go/worker/compute/committee/node.go | 236 | External batch path verifying storage signatures through the generalized committee-kind verifier. |
| go/worker/compute/committee/node.go | 662 | Batch proposal path verifying receipt signers against the storage committee via the same verifier API. |

## Code Snippets

## Snippet 1

Context: `go/roothash/api/commitment/pool.go:151` (changes signature or replay validation logic)

Before
```go
// Verify that the txn scheduler signature for current commitment is valid.
	// TODO: Also verify that the signature actually comes from a transaction
	// scheduler (similar to StorageVerifier).
	currentTxnSchedSig := body.TxnSchedSig
	if ok := body.VerifyTxnSchedSignature(blk.Header); !ok {
		return ErrTxnSchedSigInvalid
```
After
```go
// Verify that the txn scheduler signature for current commitment is valid.
	currentTxnSchedSig := body.TxnSchedSig
	if err := sv.VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, []signature.Signature{body.TxnSchedSig}); err != nil {
		logger.Debug("compute commitment has bad transaction scheduler signers",
			"committee_id", cID,
			"node_id", id,
			"err", err,
```

## Snippet 2

Context: `go/roothash/api/commitment/pool.go:32` (changes signature or replay validation logic)

Before
```go
var logger *logging.Logger = logging.GetLogger("roothash/commitment/pool")

// StorageVerifier is an interface for verifying storage receipt signatures.
type StorageVerifier interface {
	// VerifyStorageCommittee verifies that the given signatures come from the
	// current storage committee members.
	VerifyStorageCommittee(sigs []signature.Signature) error
}
```
After
```go
var logger *logging.Logger = logging.GetLogger("roothash/commitment/pool")

// SignatureVerifier is an interface for verifying storage and transaction
// scheduler signatures against the active committees.
type SignatureVerifier interface {
	// VerifyCommitteeSignatures verifies that the given signatures come from
	// the current committee members of the given kind.
	VerifyCommitteeSignatures(kind scheduler.CommitteeKind, sigs []signature.Signature) error
```

## Snippet 3

Context: `go/worker/compute/committee/node.go:236` (changes a consensus- or validator-sensitive branch)

Before
```go
// Verify storage receipt signatures.
	epoch := n.commonNode.Group.GetEpochSnapshot()
	if err := epoch.VerifyStorageCommittee(storageSignatures); err != nil {
		n.logger.Warn("received bad storage signature",
			"err", err,
```
After
```go
// Verify storage receipt signatures.
	epoch := n.commonNode.Group.GetEpochSnapshot()
	if err := epoch.VerifyCommitteeSignatures(scheduler.KindStorage, storageSignatures); err != nil {
		n.logger.Warn("received bad storage signature",
			"err", err,
```

## Snippet 4

Context: `go/worker/compute/committee/node.go:662` (changes a consensus- or validator-sensitive branch)

Before
```go
signatures = append(signatures, receipt.Signature)
		}
		if err := epoch.VerifyStorageCommittee(signatures); err != nil {
			n.logger.Error("failed to validate receipt signer",
				"err", err,
```
After
```go
signatures = append(signatures, receipt.Signature)
		}
		if err := epoch.VerifyCommitteeSignatures(scheduler.KindStorage, signatures); err != nil {
			n.logger.Error("failed to validate receipt signer",
				"err", err,
```

# Fix Pattern

Require committee-kind-aware signer authorization at the validation boundary instead of relying only on message-signature validity.

## How It Was Fixed

The fix replaced the old transaction-scheduler signature check with a call that verifies the signature against the active `scheduler.KindTransactionScheduler` committee. It also introduced a generalized verifier interface so callers specify which committee kind a signature must belong to, and updated related storage call sites to use that interface.

# Why It Matters

1. It closes a documented gap where a valid signature was not proven to come from the required committee role.

2. It strengthens a consensus-sensitive commitment admission path.

3. It makes signer authorization explicit instead of implicit in validation code.

# Evidence Notes

The strongest evidence is the removed TODO in `pool.go` stating that the code did not yet verify the signature came from a transaction scheduler, combined with the replacement call to `VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, ...)`. That is direct support for a missing role-binding flaw. The `node.go` edits show broader adoption of the same verifier API, but the provided diff does not establish a separate storage-signature vulnerability or a specific downstream exploit scenario. Protocol security invariant: A compute commitment's `TxnSchedSig` must not only be cryptographically valid for the signed message; it must also be produced by a member of the active transaction scheduler committee for the relevant round/epoch. Verification notes: The patch shows missing role membership verification for transaction-scheduler signatures, not a full proof of arbitrary outsider-key acceptance. The patch does not prove what downstream consensus impact was achievable in practice, only that an authorization check on commitment admission was incomplete. No distinct replay, nonce, or serialization flaw is demonstrated by the diff. The storage-signature call-site updates may be API unification or hardening, not evidence of a second independent vulnerability. The provided evidence directly supports a missing transaction-scheduler role-membership check. The evidence does not prove arbitrary outsider-key acceptance beyond the narrower claim that role authorization was incomplete. The evidence does not establish concrete exploitability or exact consensus impact, so confidence is kept at medium. The storage-verification changes are treated as supporting API unification/hardening rather than a distinct root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signer-authorization`
Final impact type: `unauthorized-consensus-message-acceptance`
Final tags: `consensus, signature-validation, committee-membership`

The patch is in a consensus-sensitive validation path and directly replaces a check that only validated the transaction-scheduler signature cryptographically with one that also verifies the signer belongs to the active transaction-scheduler committee. The removed TODO explicitly states that this authorization property was previously not checked. That is strong evidence of security-relevant hardening around signer authorization, but the provided diff alone does not prove a concrete exploitable vulnerability, replay condition, or end-to-end consensus compromise, so this is better retained as security-hardening rather than a fully proven security-fix.

## Security Evidence

1. Removed TODO explicitly saying the code did not verify the signature came from a transaction scheduler.
2. Commitment admission switched from VerifyTxnSchedSignature(blk.Header) to VerifyCommitteeSignatures(scheduler.KindTransactionScheduler, ...).
3. A new committee-kind-aware verifier interface makes role membership part of signature acceptance.
4. The affected code sits in roothash commitment and committee processing, which are consensus-sensitive paths.

## Missing Evidence

1. The provided patch does not include the implementation of VerifyTxnSchedSignature, so the exact pre-fix guarantees are not fully visible.
2. No concrete exploit, outsider-key acceptance trace, or consensus-failure scenario is shown in the diff.
3. The referenced tests are not included in the evidence, so regression coverage cannot be assessed directly.

## Claim Boundaries

1. The evidence supports a missing committee-role authorization check for transaction-scheduler signatures.
2. The evidence does not prove replay as the specific bug class.
3. The storage-signature call-site updates should be treated as related API hardening, not a separately demonstrated vulnerability.
4. Impact should be described conservatively as reducing risk of unauthorized signer acceptance in consensus logic, not as a proven end-to-end exploit.
