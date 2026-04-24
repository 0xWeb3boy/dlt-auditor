---
case_id: case_20260219_1a3758d85
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2026-02-19
source_refs:
  - git:1a3758d85aaec7d38e871766c330c76e36a5dcf0
  - "sei-tendermint/internal/autobahn/types/proposal.go:170"
  - "sei-tendermint/internal/autobahn/data/testonly.go:74"
  - "sei-tendermint/internal/autobahn/avail/state_test.go:34"
  - "sei-tendermint/internal/autobahn/types/proposal.go:228"
bug_class: consensus-proposal-validation-hardening
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - proposal-validation
  - leader-validation
  - committee-lane-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to harden consensus proposal validation. The directly shown code adds proposal-level lane-range validation and rejects `NewProposal` calls made with a key that is not the view leader. The commit summary additionally claims `FullProposal.Verify` now verifies the actual proposer signature and LaneQC header hash consistency, but those specific implementation hunks are not included in the provided evidence.

## Observed Patch Facts

1. In `sei-tendermint/internal/autobahn/types/proposal.go`, the patch replaces `// LaneRange returns the range of blocks of the given lane.` with `// Verify checks that every present lane range belongs to the committee`.

2. In `sei-tendermint/internal/autobahn/data/testonly.go`, the patch replaces `proposal, err := types.NewProposal(` with `leader := committee.Leader(viewSpec.View())`.

3. In `sei-tendermint/internal/autobahn/avail/state_test.go`, the patch replaces `func makeCommitQC(` with `func leaderKey(committee *types.Committee, keys []types.SecretKey, view types.View) t...`.

4. In `sei-tendermint/internal/autobahn/types/proposal.go`, the patch adds `if got, want := key.Public(), committee.Leader(viewSpec.View()); got != want {`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/autobahn/types`, `sei-tendermint/internal/autobahn`, `sei-tendermint/internal/autobahn/data`, which anchors the finding in the `cryptography` area of the project. Historical context from `sei-tendermint/internal/autobahn/types/committee.go`, `sei-tendermint/internal/autobahn/types/types_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/autobahn/types/proposal_test.go`, `sei-tendermint/internal/autobahn/avail/inner_test.go`. The strongest project-level identifiers around this patch are `types`, `committee`, `viewSpec`, and `leader`.

## Before/After Behavior

Before the patch, the shown `NewProposal` body did not reject a non-leader key before constructing or reproposing a proposal, and the shown `Proposal` code did not include a proposal-level `Verify` method for present lane ranges. After the patch, `NewProposal` compares `key.Public()` to `committee.Leader(viewSpec.View())` and returns an error on mismatch, while `Proposal.Verify(c)` iterates over present lane ranges and calls `LaneRange.Verify(c)`. Test helpers were updated to choose the actual leader key before creating proposals. Signature and LaneQC hash behavior is supported by the commit summary only, not by shown code hunks.

# Root Cause

Proposal validation relied on assumptions or narrower checks at consensus proposal boundaries. The shown root causes are missing fail-fast enforcement that the constructor key is the view leader and missing proposal-level validation of lane ranges against the committee. Additional claimed gaps in signature and LaneQC hash verification are plausible from the commit summary but not independently shown in the supplied code excerpts.

## Walkthrough

1. `NewProposal` receives a signing key, committee, view specification, lane QCs, and optional app QC.

2. The patch adds a check that the supplied key's public key equals the committee leader for the proposal view.

3. If the key is not the leader key, construction now fails with an error.

4. The patch adds `Proposal.Verify(c *Committee)` for validating present lane ranges.

5. `Proposal.Verify` delegates each lane range to `LaneRange.Verify(c)` and wraps errors with the lane identifier.

6. Test-only proposal construction was adjusted to select the leader key, matching the stricter constructor behavior.

7. The commit summary says `FullProposal.Verify` was also tightened for proposer signatures and LaneQC hash consistency, but the provided hunks do not show that code path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/autobahn/types/proposal.go | 170 | Adds `Proposal.Verify` to reject lane ranges that are not valid for the committee before full proposal acceptance. |
| sei-tendermint/internal/autobahn/types/proposal.go | 228 | Adds leader public-key validation in `NewProposal` so proposals cannot be constructed with a non-leader signing key for the view. |
| sei-tendermint/internal/autobahn/data/testonly.go | 74 | Updates test proposal construction to use the actual view leader key after constructor validation became stricter. |
| sei-tendermint/internal/autobahn/avail/state_test.go | 34 | Adds test helper for selecting the leader key, reflecting the enforced leader invariant in test paths. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/autobahn/types/proposal.go:170` (changes signature or replay validation logic)

Before
```go
}

// LaneRange returns the range of blocks of the given lane.
func (m *Proposal) LaneRange(lane LaneID) *LaneRange {
```
After
```go
}

// Verify checks that every present lane range belongs to the committee
// and is internally valid. Lanes may be omitted — omitted lanes are
// treated as implicit empty ranges by FullProposal.Verify.
func (m *Proposal) Verify(c *Committee) error {
	for _, r := range m.laneRanges {
		if err := r.Verify(c); err != nil {
```

## Snippet 2

Context: `sei-tendermint/internal/autobahn/data/testonly.go:74` (changes a sensitive control or state-update path)

Before
```go
}
	viewSpec := types.ViewSpec{CommitQC: prev}
	proposal, err := types.NewProposal(
		types.GenSecretKey(rng),
		committee,
		viewSpec,
```
After
```go
}
	viewSpec := types.ViewSpec{CommitQC: prev}
	leader := committee.Leader(viewSpec.View())
	var leaderKey types.SecretKey
	for _, k := range keys {
		if k.Public() == leader {
			leaderKey = k
			break
```

## Snippet 3

Context: `sei-tendermint/internal/autobahn/avail/state_test.go:34` (changes a sensitive control or state-update path)

Before
```go
}

func makeCommitQC(
	rng utils.Rng,
```
After
```go
}

func leaderKey(committee *types.Committee, keys []types.SecretKey, view types.View) types.SecretKey {
	leader := committee.Leader(view)
	for _, k := range keys {
		if k.Public() == leader {
			return k
		}
```

## Snippet 4

Context: `sei-tendermint/internal/autobahn/types/proposal.go:228` (changes a sensitive control or state-update path)

Before
```go
appQC utils.Option[*AppQC],
) (*FullProposal, error) {
	if p, ok := NewReproposal(key, viewSpec); ok {
		return p, nil
```
After
```go
appQC utils.Option[*AppQC],
) (*FullProposal, error) {
	if got, want := key.Public(), committee.Leader(viewSpec.View()); got != want {
		return nil, fmt.Errorf("key %q is not the leader %q for view %v", got, want, viewSpec.View())
	}
	if p, ok := NewReproposal(key, viewSpec); ok {
		return p, nil
```

# Fix Pattern

Move consensus proposal invariants into explicit construction and verification checks instead of relying on surrounding code to supply valid leader keys, committee lanes, signatures, or hash-linked data.

## How It Was Fixed

`proposal.go` now rejects `NewProposal` calls where the key is not the leader for `viewSpec.View()`. It also adds `Proposal.Verify(c)`, which validates each present lane range through `LaneRange.Verify(c)`. Test helpers in `data/testonly.go` and `avail/state_test.go` were updated to locate the correct leader key before constructing proposals. Claimed `FullProposal.Verify` signature and LaneQC hash checks are accepted only as commit-message evidence.

# Why It Matters

1. Consensus proposal acceptance is security-sensitive.

2. Non-leader proposal construction is now rejected in the shown code.

3. Invalid committee lane ranges are now rejectable through `Proposal.Verify`.

4. The evidence does not prove a concrete exploit, fork, or funds impact.

# Evidence Notes

Strongest direct evidence is in `sei-tendermint/internal/autobahn/types/proposal.go`: the added leader check in `NewProposal` and the new `Proposal.Verify` method. Test file changes support that the constructor behavior changed. The commit summary is relevant and specific, but the provided code excerpts do not show the `FullProposal.Verify` signature or LaneQC hash changes, nor do they show the call site proving `Proposal.Verify` is invoked during received proposal verification. Therefore the finding should not claim a proven exploit or confirmed full validation bypass. Protocol security invariant: Autobahn consensus proposals should only pass construction and verification when they are tied to the correct view leader, contain lane ranges valid for the committee, and, per the commit summary, have valid proposer signatures and LaneQC hash linkage. Verification notes: The patch evidence does not show a complete exploit path against a live network. The exact pre-patch `FullProposal.Verify` implementation is not included, so signature and LaneQC hash details rely on the provided commit summary. No specific consensus safety violation, fork, or funds impact is proven by the provided patch context. Test-only changes are supporting evidence and are not themselves security fixes. Directly verified from provided hunks: leader-key validation was added to `NewProposal`. Directly verified from provided hunks: `Proposal.Verify` validates present lane ranges with `LaneRange.Verify(c)`. Not directly shown: `FullProposal.Verify` actual signature verification implementation. Not directly shown: LaneQC header hash comparison implementation. Not proven: live-network exploitability, safety failure, fork, or funds loss. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-proposal-validation-hardening`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, proposal-validation, leader-validation, committee-lane-validation, security-hardening`

The supplied evidence supports retaining this as security hardening, not a proven security fix. The direct hunks add stricter validation in a consensus proposal path: proposals now expose lane-range verification against the committee, and NewProposal rejects keys that are not the leader for the view. The commit metadata also specifically frames this as hardening against malicious proposals and claims signature and hash-link checks, but those stronger FullProposal.Verify changes are not shown, so the corpus entry should avoid claiming a confirmed exploitable validation bypass.

## Security Evidence

1. New Proposal construction now checks key.Public() against committee.Leader(viewSpec.View()) and errors on mismatch.
2. A Proposal.Verify(c) method was added to validate every present lane range with LaneRange.Verify(c).
3. The changed files are in the Autobahn consensus/types proposal path, which is security-sensitive.
4. Test helpers were updated to select the actual leader key, supporting that non-leader proposal construction became invalid.
5. Commit subject and body explicitly describe hardening against malicious proposals and missing proposer signature verification.

## Missing Evidence

1. The provided hunks do not show the claimed FullProposal.Verify proposer signature verification change.
2. The provided hunks do not show the claimed LaneQC header hash comparison.
3. The evidence does not show where Proposal.Verify is invoked on externally received proposals.
4. No exploit path, fork scenario, funds impact, or concrete attacker workflow is demonstrated.

## Claim Boundaries

1. Classify as consensus proposal validation hardening, not a confirmed exploitable vulnerability fix.
2. Do not claim proven signature-bypass remediation from the shown code alone.
3. Do not claim proven live-network consensus failure or financial impact.
4. Test-only changes are supporting evidence for stricter invariants, not standalone security fixes.
