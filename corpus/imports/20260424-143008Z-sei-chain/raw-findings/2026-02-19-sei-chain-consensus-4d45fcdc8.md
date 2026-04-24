---
case_id: case_20260219_4d45fcdc8
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2026-02-19
source_refs:
  - git:4d45fcdc8854e53e7cba3821851f591f704d6aa6
  - "sei-tendermint/internal/autobahn/data/state.go:145"
  - "sei-tendermint/internal/autobahn/data/state_test.go:111"
  - "sei-tendermint/internal/autobahn/data/state_test.go:7"
bug_class: improper-consensus-state-validation
impact_type:
  - state-integrity
  - local-availability
confidence: medium
tags:
  - consensus
  - quorum-certificate
  - input-validation
  - state-integrity
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a security-relevant state-integrity issue in the Autobahn consensus data path. Before the fix, PushQC could use a stale or unneeded incoming QC's range and headers during later mutation and block matching even though QC verification was only performed when needQC was true. The fix ties QC insertion and update signaling to needQC, and matches blocks against stored verified QC headers.

## Observed Patch Facts

1. In `sei-tendermint/internal/autobahn/data/state.go`, the patch replaces `if inner.nextQC < gr.Next {` with `if needQC {`.

2. In `sei-tendermint/internal/autobahn/data/state_test.go`, the patch replaces `func TestExecution(t *testing.T) {` with `func TestPushQCStaleQCDoesNotCorruptState(t *testing.T) {`.

3. In `sei-tendermint/internal/autobahn/data/state_test.go`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/autobahn/data`, `sei-tendermint/internal/autobahn`, which anchors the finding in the `consensus` area of the project. Historical context from `sei-tendermint/internal/autobahn/data/testonly.go`, `sei-tendermint/internal/autobahn/consensus/persisted_inner.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/autobahn/data/testonly.go`, `sei-tendermint/internal/autobahn/consensus/state.go`. The strongest project-level identifiers around this patch are `inner`, `nextQC`, `utils`, and `Next`.

## Before/After Behavior

Before the patch, PushQC computed needQC and verified the QC only on that path, but the atomic update later used inner.nextQC < gr.Next to decide whether to call ctrl.Updated() and insert the incoming QC. This allowed stale or unneeded QCs to affect nextQC/update behavior. The block path also used headers from the incoming QC, which could be unverified in stale/unneeded cases. After the patch, QC insertion and ctrl.Updated() are guarded by needQC, block matching uses stored verified QC headers, and the block loop is bounded by locally available stored QC state.

# Root Cause

PushQC separated the needed-and-verified QC decision from later state mutation and block matching. The later logic could still rely on the incoming QC's range or headers even when that QC was stale or not verified on the current path.

## Walkthrough

1. PushQC receives a FullCommitQC and blocks, derives the QC global range, and computes whether the QC is currently needed.

2. The QC is verified only when needQC is true.

3. Before the fix, the later locked mutation used inner.nextQC < gr.Next rather than needQC to decide whether to update state and insert the QC.

4. That meant a stale or unneeded QC range could still advance stored QC state or trigger update notifications.

5. Before the fix, blocks were matched against headers associated with the incoming QC, which the commit identifies as unverified in the stale/unneeded case.

6. The fix places QC insertion and ctrl.Updated() under if needQC.

7. The fix changes block matching to use stored verified QC headers on a per-block basis.

8. The fix also bounds insertion by stored QC availability, addressing the nil-pointer path described in the commit message.

9. Regression tests cover stale malicious QCs, tampered headers, absence of panic, lack of state corruption, and later acceptance of valid data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/autobahn/data/state.go | 115 | PushQC receives a FullCommitQC and blocks, decides whether the QC is needed, verifies the QC only on the needed path, verifies blocks, then atomically updates stored QCs and blocks. |
| sei-tendermint/internal/autobahn/data/state.go | 145 | QC insertion and ctrl.Updated() are now guarded by needQC so stale QCs cannot advance nextQC or cause spurious state updates; block insertion is bounded and matched against stored verified QC headers. |
| sei-tendermint/internal/autobahn/data/state_test.go | 111 | Regression test constructs stale or tampered QC scenarios and asserts no state corruption, no panic, rejection of fake blocks, and later acceptance of valid QCs and blocks. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/autobahn/data/state.go:145` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Atomically insert QC and blocks.
	for inner, ctrl := range s.inner.Lock() {
		if inner.nextQC < gr.Next {
			ctrl.Updated()
		}
		for inner.nextQC < gr.Next {
			inner.qcs[inner.nextQC] = qc
			inner.nextQC += 1
```
After
```go
// Atomically insert QC and blocks.
	for inner, ctrl := range s.inner.Lock() {
		if needQC {
			for inner.nextQC < gr.Next {
				inner.qcs[inner.nextQC] = qc
				inner.nextQC += 1
			}
			ctrl.Updated()
```

## Snippet 2

Context: `sei-tendermint/internal/autobahn/data/state_test.go:111` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func TestExecution(t *testing.T) {
	ctx := t.Context()
```
After
```go
}

func TestPushQCStaleQCDoesNotCorruptState(t *testing.T) {
	ctx := t.Context()
	rng := utils.TestRng()
	committee, keys := types.GenCommittee(rng, 3)
	state := NewState(&Config{
		Committee: committee,
```

## Snippet 3

Context: `sei-tendermint/internal/autobahn/data/state_test.go:7` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
"maps"
	"testing"

	"github.com/sei-protocol/sei-chain/sei-tendermint/internal/autobahn/types"
	"github.com/sei-protocol/sei-chain/sei-tendermint/libs/utils"
	"github.com/sei-protocol/sei-chain/sei-tendermint/libs/utils/scope"
)
```
After
```go
"maps"
	"testing"
	"time"

	"github.com/sei-protocol/sei-chain/sei-tendermint/internal/autobahn/types"
	"github.com/sei-protocol/sei-chain/sei-tendermint/libs/utils"
	"github.com/sei-protocol/sei-chain/sei-tendermint/libs/utils/require"
	"github.com/sei-protocol/sei-chain/sei-tendermint/libs/utils/scope"
```

# Fix Pattern

Use the same validation predicate for both verification and mutation, and validate dependent data against canonical locally stored verified state rather than untrusted incoming metadata.

## How It Was Fixed

In state.go, QC insertion, nextQC advancement, and ctrl.Updated() were moved under the needQC guard. The block insertion path was changed to compare blocks with stored verified QC headers instead of the incoming QC headers, and to avoid iterating beyond available stored QC state. Tests were added in state_test.go for stale-QC state corruption and tampered-header rejection.

# Why It Matters

1. Protects consensus data state from stale QC mutation.

2. Prevents update notifications from unneeded QCs.

3. Avoids trusting headers from an unverified incoming QC for block matching.

4. Removes a nil-pointer availability failure for overextended QC ranges.

5. Does not require claiming finalized-chain divergence or network-wide denial of service.

# Evidence Notes

The strongest evidence is the PushQC diff in sei-tendermint/internal/autobahn/data/state.go, where needQC is computed, QC verification is conditional, and the mutation path is changed to guard QC insertion and ctrl.Updated() with needQC. The commit message explicitly describes stale malicious QCs, tampered headers, state corruption, fake block rejection, and a nil-pointer failure mode. The tests in sei-tendermint/internal/autobahn/data/state_test.go support those scenarios. The evidence does not prove unauthenticated remote reachability, finalized-chain divergence, economic loss, or validator key compromise. Protocol security invariant: PushQC should only let a needed, verified quorum certificate mutate stored QC state, advance nextQC, or trigger state-update notifications. Block insertion for a QC range should be checked against locally stored verified QC headers, not headers from a stale or otherwise unneeded incoming QC. Verification notes: The patch does not prove that an unauthenticated remote peer can reach PushQC directly. The patch does not prove consensus safety failure such as finalized-chain divergence. The patch does not prove economic loss or validator key compromise. The nil-pointer path supports an availability concern, but the provided evidence does not quantify network-wide denial-of-service impact. The stale QC behavior shows state corruption risk inside this data path, but broader propagation through the full protocol is not shown. Patch is implementation code plus focused regression tests, not only cleanup or refactor. Security relevance is supported by consensus data mutation, verification bypass conditions, and malicious/tampered QC test cases. Impact should be bounded to PushQC state integrity and local availability based on the provided evidence. Broader protocol exploitability is not established by the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-consensus-state-validation`
Final impact type: `state-integrity, local-availability`
Final confidence: `medium`
Final tags: `consensus, quorum-certificate, input-validation, state-integrity, availability`

The supplied evidence supports retaining this as security hardening in a consensus data path. The patch ties QC mutation and update signaling to the same needQC condition that gates verification, avoids matching blocks against headers from an unverified incoming QC, and bounds iteration to avoid a nil-pointer path. That is security-sensitive behavior around verified consensus certificates, but the evidence does not prove remote reachability, full protocol exploitability, or finalized-chain divergence strongly enough to keep the original high-confidence security-fix framing.

## Security Evidence

1. PushQC verifies the QC only when needQC is true, and the patch makes QC insertion and ctrl.Updated() use that same guard.
2. The patch changes block matching to use stored, already verified QC headers instead of headers from the incoming QC.
3. The commit and tests describe stale malicious QCs, tampered headers, fake block rejection, and preventing state corruption.
4. The changed code is in a Tendermint/Autobahn consensus data path handling quorum certificates and blocks.
5. The patch caps the insertion loop to avoid a nil-pointer failure when a malicious QC range extends beyond stored QCs.

## Missing Evidence

1. No proof that an unauthenticated remote attacker can directly reach PushQC.
2. No demonstrated finalized-chain divergence or network-wide consensus safety failure.
3. No evidence of economic loss, validator key compromise, or privilege escalation.
4. The nil-pointer path supports availability risk, but the scope of denial of service is not established.

## Claim Boundaries

1. Validated as consensus security hardening, not a fully proven exploitable security fix.
2. Impact should be limited to PushQC state integrity and local availability based on the supplied evidence.
3. Do not claim client-view divergence or finalized-chain divergence from this patch alone.
4. Do not claim broad remote exploitability without additional call-path or threat-model evidence.
