---
case_id: case_20190722_079912fe5
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2019-07-22
source_refs:
  - git:079912fe5c53aeddb2ba49d2b5b1c2787eb4664b
  - "go/worker/common/committee/group.go:161"
  - "go/worker/common/committee/group.go:240"
  - "go/worker/compute/committee/node.go:214"
  - "go/worker/compute/committee/node.go:623"
bug_class: missing-signer-authorization-check
impact_type:
  - unauthorized-signature-acceptance
confidence: medium
tags:
  - cryptography
  - signature-validation
  - committee-membership
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit authorization check for storage receipt signers. Before it, the shown compute-committee paths accepted storage receipt signatures without the demonstrated check that the signer belonged to the current storage committee. After it, those paths reject signatures whose public keys are not in the active epoch's storage committee set.

## Observed Patch Facts

1. In `go/worker/common/committee/group.go`, the patch replaces `// Group encapsulates communication with a group of nodes in the` with `// VerifyStorageCommittee verifies that the given signatures come from the`.

2. In `go/worker/common/committee/group.go`, the patch replaces `determineRole := func(c *scheduler.Committee) (nodes []*node.Node, leader int, role s...` with `// Find the current committees.`.

3. In `go/worker/compute/committee/node.go`, the patch replaces `// TODO: Actually check that the storage receipts were signed by storage` with `epoch := n.commonNode.Group.GetEpochSnapshot()`.

4. In `go/worker/compute/committee/node.go`, the patch replaces `proposedResults.StorageSignatures = signatures` with `if err := epoch.VerifyStorageCommittee(signatures); err != nil {`.

## Project Context

The changed code sits primarily in `go/worker/common/committee`, `go/worker/common`, `go/worker/compute/committee`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/worker/common/committee/node.go`, `go/worker/compute/committee/state.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/common/committee/node.go`, `go/worker/compute/worker.go`. The strongest project-level identifiers around this patch are `storage`, `signatures`, `signature`, and `VerifyStorageCommittee`. Nearby tests or test-like files include `go/worker/compute/tests/tester.go`.

## Before/After Behavior

Before the patch, the provided `queueBatchBlocking` excerpt contained a TODO stating storage receipts were not actually checked to confirm they were signed by storage nodes, and `proposeBatchLocked` collected receipt signatures without the shown membership validation. After the patch, `EpochSnapshot.VerifyStorageCommittee` checks each signature's public key against `e.storageCommittee.PublicKeys`, and both shown compute paths call that verifier and fail on non-member signers.

# Root Cause

Authorization of storage receipt signers was incomplete at the compute/storage boundary: the shown code treated attached signatures as acceptable without the demonstrated enforcement that the signer belonged to the current epoch's authorized storage committee.

## Walkthrough

1. `go/worker/common/committee/group.go` adds `EpochSnapshot.VerifyStorageCommittee(sigs []signature.Signature)`, which iterates over signatures and errors if a signer's public key is not in `e.storageCommittee.PublicKeys`.

2. `Group.EpochTransition` is updated in the shown area to track `storageCommittee` in the active epoch snapshot, supplying the verifier with the current authorized signer set.

3. In `go/worker/compute/committee/node.go:queueBatchBlocking`, the code now gets the epoch snapshot and calls `epoch.VerifyStorageCommittee(storageSignatures)` before continuing.

4. If that check fails, `queueBatchBlocking` logs a bad storage signature and returns `errInvalidReceipt`.

5. In `go/worker/compute/committee/node.go:proposeBatchLocked`, the code now validates collected receipt signatures with the same verifier before proceeding.

6. If that proposer-side check fails, the function logs the signer validation failure and returns an error.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/common/committee/group.go | 161 | adds epoch-scoped verifier that rejects signatures from keys outside the current storage committee |
| go/worker/common/committee/group.go | 240 | tracks current storage committee membership during epoch transition so signer authorization can be evaluated |
| go/worker/compute/committee/node.go | 214 | rejects externally queued batches when attached storage receipt signers are not authorized storage committee members |
| go/worker/compute/committee/node.go | 623 | rejects proposed batch results when collected storage receipts are signed by unauthorized members |

## Code Snippets

## Snippet 1

Context: `go/worker/common/committee/group.go:161` (changes signature or replay validation logic)

Before
```go
}

// Group encapsulates communication with a group of nodes in the
// compute committee.
```
After
```go
}

// VerifyStorageCommittee verifies that the given signatures come from the
// current storage committee members.
//
// Implements commitment.StorageVerifier.
func (e *EpochSnapshot) VerifyStorageCommittee(sigs []signature.Signature) error {
	for _, sig := range sigs {
```

## Snippet 2

Context: `go/worker/common/committee/group.go:240` (changes an authorization or privilege gate)

Before
```go
publicIdentity := g.identity.NodeSigner.Public()

	determineRole := func(c *scheduler.Committee) (nodes []*node.Node, leader int, role scheduler.Role, err error) {
		leader = -1

		for idx, node := range c.Members {
			if node.PublicKey.Equal(publicIdentity) {
				role = node.Role
```
After
```go
publicIdentity := g.identity.NodeSigner.Public()

	// Find the current committees.
	computeCommittees := make(map[hash.Hash]*CommitteeInfo)
	computeCommitteesByPeer := make(map[signature.MapKey]bool)
	var computeCommittee, txnSchedulerCommittee, mergeCommittee, storageCommittee *CommitteeInfo
	var computeCommitteeID hash.Hash
	var txnSchedulerLeaderPeerID signature.PublicKey
```

## Snippet 3

Context: `go/worker/compute/committee/node.go:214` (changes signature or replay validation logic)

Before
```go
}

	// TODO: Actually check that the storage receipts were signed by storage
	// nodes: https://github.com/oasislabs/ekiden/issues/1809.

	// Verify storage receipt signatures.
	receiptBody := storage.ReceiptBody{
		Version:   1,
```
After
```go
}

	// Verify storage receipt signatures.
	epoch := n.commonNode.Group.GetEpochSnapshot()
	if err := epoch.VerifyStorageCommittee(storageSignatures); err != nil {
		n.logger.Warn("received bad storage signature",
			"err", err,
		)
```

## Snippet 4

Context: `go/worker/compute/committee/node.go:623` (changes a consensus- or validator-sensitive branch)

Before
```go
signatures = append(signatures, receipt.Signature)
		}
		proposedResults.StorageSignatures = signatures
```
After
```go
signatures = append(signatures, receipt.Signature)
		}
		if err := epoch.VerifyStorageCommittee(signatures); err != nil {
			n.logger.Error("failed to validate receipt signer",
				"err", err,
			)
			return err
		}
```

# Fix Pattern

Add an epoch-scoped signer-authorization helper and invoke it at receipt-ingestion points so unauthorized signers are rejected before their signatures influence protocol processing.

## How It Was Fixed

The fix introduced a helper on the epoch snapshot that checks whether each signature belongs to a current storage committee member, then wired that helper into the two shown compute-committee receipt paths so they reject non-member signers immediately.

# Why It Matters

1. It enforces that receipt authorization depends on committee membership, not just the presence of a signature object.

2. It closes a validation gap explicitly acknowledged by the pre-patch TODO in the shown external batch path.

3. It prevents non-storage-committee identities from being accepted in the shown receipt-handling paths.

# Evidence Notes

Direct evidence supports a signer-membership check, not broader claims about replay prevention, threshold logic, duplicate signer handling, or exploit impact. The strongest proof is the new `VerifyStorageCommittee` method plus its new use in `queueBatchBlocking` and `proposeBatchLocked`. The commit subject and TODO make the intent clear, but the provided excerpts do not by themselves establish how far an unauthorized signer could have progressed in consensus beyond the shown paths. Protocol security invariant: Storage receipt signatures accepted by compute-committee code must come from members of the current storage committee for the active epoch; signatures from non-members must be rejected before batch acceptance or proposal assembly. Verification notes: The patch proves signer-membership enforcement, not the full cryptographic verification flow for each receipt. The patch does not show whether quorum size, duplicate signer handling, or threshold rules were also changed. The patch does not by itself prove finalized consensus corruption or a practical exploit path. The patch only demonstrates current-committee binding; broader replay resistance across epochs is not fully established here. The patch clearly adds membership validation against the current storage committee. The provided evidence does not show changes to cryptographic signature verification itself. The provided evidence does not show quorum, uniqueness, or cross-epoch replay checks. Security classification is based on a newly enforced authorization invariant in consensus-adjacent code, with exploitability not fully demonstrated in the excerpts. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signer-authorization-check`
Final impact type: `unauthorized-signature-acceptance`
Final confidence: `medium`
Final tags: `cryptography, signature-validation, committee-membership, consensus`

The patch clearly adds a missing authorization check in a security-sensitive, consensus-adjacent path: storage receipt signatures must now come from members of the current storage committee, and invalid signers are rejected. That supports retaining this as a security-relevant case. However, the provided patch does not by itself prove a concrete exploitable vulnerability, replay condition, or finalized state compromise, so the safer classification is security hardening rather than a confirmed security fix.

## Security Evidence

1. A pre-patch TODO explicitly says storage receipts were not actually checked to be signed by storage nodes.
2. New `VerifyStorageCommittee` code rejects signatures whose public keys are not in the current storage committee set.
3. `queueBatchBlocking` now validates storage signers and returns `errInvalidReceipt` on failure.
4. `proposeBatchLocked` now validates collected receipt signers and aborts on failure.
5. Epoch transition logic now tracks the active `storageCommittee`, enabling epoch-scoped signer authorization.

## Missing Evidence

1. The excerpts do not show that unauthorized signers could previously cause finalized consensus or state corruption.
2. The excerpts do not show quorum, uniqueness, or duplicate-signer validation behavior.
3. The excerpts do not show a replay attack or any cross-epoch misuse beyond committee-membership checking.
4. The excerpts do not prove whether cryptographic signature verification itself was absent or only signer authorization was missing.

## Claim Boundaries

1. Supported: the patch enforces that receipt signers belong to the current storage committee.
2. Supported: unauthorized signer acceptance in shown receipt-handling paths is now rejected.
3. Not supported: this patch proves a replay vulnerability.
4. Not supported: this patch proves a concrete exploitable consensus break or state-compromise bug.
