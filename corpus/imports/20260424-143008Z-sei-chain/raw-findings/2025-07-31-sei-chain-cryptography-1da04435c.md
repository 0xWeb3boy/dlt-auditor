---
case_id: case_20250731_1da04435c
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
bug_class: resource-exhaustion
confidence: medium
source_quality: high
date: 2025-07-31
source_refs:
  - git:1da04435c86e66d2f4c6736dbdbcaaee11c7a667
  - "sei-tendermint/types/part_set.go:203"
  - "sei-tendermint/internal/consensus/state.go:2396"
  - "sei-tendermint/internal/consensus/reactor_test.go:1033"
  - "sei-tendermint/internal/consensus/peer_state.go:110"
impact_type:
  - availability
  - resource-exhaustion
tags:
  - infrastructure
  - consensus
  - resource-exhaustion
  - memory-limit
  - bounds-check
  - input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds bounds checks for excessive PartSetHeader.Total values in Tendermint consensus proposal and peer-state handling, plus a defensive fallback in NewPartSetFromHeader. The supported security thesis is resource-exhaustion prevention from oversized consensus block-part counts. The evidence does not support cryptographic, replay, signature-bypass, or consensus-safety claims beyond resource-control risk.

## Observed Patch Facts

1. In `sei-tendermint/types/part_set.go`, the patch replaces `total: header.Total,` with `if header.Total > MaxBlockPartsCount {`.

2. In `sei-tendermint/internal/consensus/state.go`, the patch replaces `cs.roundState.SetProposalBlockParts(types.NewPartSetFromHeader(proposal.BlockID.PartS...` with `// apply the same check as in SetHasProposal`.

3. In `sei-tendermint/internal/consensus/reactor_test.go`, the patch adds `func TestReactorMemoryLimitCoverage(t *testing.T) {`.

4. In `sei-tendermint/internal/consensus/peer_state.go`, the patch replaces `ps.mtx.Lock()` with `// ignore nil proposals`.

## Project Context

The changed code sits primarily in `sei-tendermint/types`, `sei-tendermint/internal/consensus`, `sei-tendermint/internal`, which anchors the finding in the `cryptography` area of the project. Historical context from `sei-tendermint/types/proposal_test.go`, `sei-tendermint/internal/consensus/peer_state_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/consensus/peer_state_test.go`, `sei-tendermint/internal/consensus/msgs_test.go`. The strongest project-level identifiers around this patch are `proposal`, `Total`, `PartSet`, and `PartSetHeader`. Nearby tests or test-like files include `sei-tendermint/internal/consensus/wal_fuzz.go`, `sei-tendermint/internal/test/factory/block.go`.

## Before/After Behavior

Before the patch, NewPartSetFromHeader accepted header.Total directly, and defaultSetProposal could call NewPartSetFromHeader on a proposal's PartSetHeader without a local MaxBlockPartsCount rejection. PeerState.SetHasProposal also lacked the shown early nil and over-limit Total checks. After the patch, over-limit proposal part counts are rejected in defaultSetProposal, ignored in SetHasProposal, and handled defensively in NewPartSetFromHeader by returning a minimal safe PartSet.

# Root Cause

A consensus proposal's PartSetHeader.Total was not consistently checked against MaxBlockPartsCount before being used in proposal block-part setup or peer proposal-state handling.

## Walkthrough

1. A proposal includes BlockID.PartSetHeader.Total, which controls how many block parts are expected.

2. The previous NewPartSetFromHeader path accepted header.Total directly.

3. The proposal path could initialize ProposalBlockParts from that header without the new explicit MaxBlockPartsCount check shown in defaultSetProposal.

4. The peer-state path similarly lacked the shown early rejection for over-limit Total values.

5. The patch rejects excessive Total in defaultSetProposal with ErrInvalidProposalPartSetHeader.

6. The patch makes SetHasProposal return early for nil proposals and for proposals whose Total exceeds MaxBlockPartsCount.

7. The patch adds a defensive guard in NewPartSetFromHeader so oversized direct constructor use no longer follows the normal header.Total path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/types/part_set.go | 203 | defensive bound in PartSet construction from PartSetHeader before allocating part tracking structures |
| sei-tendermint/internal/consensus/state.go | 2396 | proposal acceptance path rejects PartSetHeader.Total greater than MaxBlockPartsCount before setting ProposalBlockParts |
| sei-tendermint/internal/consensus/peer_state.go | 110 | peer proposal state path ignores nil proposals and refuses proposals with excessive PartSetHeader.Total before state mutation |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/types/part_set.go:203` (changes signature or replay validation logic)

Before
```go
// Returns an empty PartSet ready to be populated.
func NewPartSetFromHeader(header PartSetHeader) *PartSet {
	return &PartSet{
		total:         header.Total,
```
After
```go
// Returns an empty PartSet ready to be populated.
func NewPartSetFromHeader(header PartSetHeader) *PartSet {
	if header.Total > MaxBlockPartsCount {
		log.Warn().Msgf("Attempted to create PartSet with excessive Total: %d (max: %d). Creating minimal safe PartSet instead.", header.Total, MaxBlockPartsCount)
		return &PartSet{
			total:         1,           // Minimal safe size
			hash:          header.Hash, // Keep original hash for compatibility
			parts:         make([]*Part, 1),
```

## Snippet 2

Context: `sei-tendermint/internal/consensus/state.go:2396` (changes a sensitive control or state-update path)

Before
```go
// TODO: We can check if Proposal is for a different block as this is a sign of misbehavior!
	if cs.roundState.ProposalBlockParts() == nil {
		cs.metrics.MarkBlockGossipStarted()
		cs.roundState.SetProposalBlockParts(types.NewPartSetFromHeader(proposal.BlockID.PartSetHeader))
```
After
```go
// TODO: We can check if Proposal is for a different block as this is a sign of misbehavior!
	if cs.roundState.ProposalBlockParts() == nil {
		// apply the same check as in SetHasProposal
		if proposal.BlockID.PartSetHeader.Total > types.MaxBlockPartsCount {
			cs.logger.Debug("rejecting proposal with too many parts", "total", proposal.BlockID.PartSetHeader.Total, "max", types.MaxBlockPartsCount)
			return ErrInvalidProposalPartSetHeader
		}
		cs.metrics.MarkBlockGossipStarted()
```

## Snippet 3

Context: `sei-tendermint/internal/consensus/reactor_test.go:1033` (changes signature or replay validation logic)

Before
```go
}
}
```
After
```go
}
}

func TestReactorMemoryLimitCoverage(t *testing.T) {
	// This test covers the error handling paths in reactor when proposals exceed memory limits
	// It's designed to improve test coverage for the reactor's proposal validation

	logger := log.NewTestingLogger(t)
```

## Snippet 4

Context: `sei-tendermint/internal/consensus/peer_state.go:110` (changes a sensitive control or state-update path)

Before
```go
// SetHasProposal sets the given proposal as known for the peer.
func (ps *PeerState) SetHasProposal(proposal *types.Proposal) {
	ps.mtx.Lock()
	defer ps.mtx.Unlock()
```
After
```go
// SetHasProposal sets the given proposal as known for the peer.
func (ps *PeerState) SetHasProposal(proposal *types.Proposal) {
	// ignore nil proposals
	if proposal == nil {
		return
	}

	// Check memory limits before acquiring lock or setting any state
```

# Fix Pattern

Validate externally supplied consensus sizing fields before they can affect allocation-sized structures or consensus peer/proposal state, and add a lower-level defensive guard for missed callers.

## How It Was Fixed

The fix added MaxBlockPartsCount checks in defaultSetProposal and PeerState.SetHasProposal. It also changed NewPartSetFromHeader so an oversized header.Total returns a minimal PartSet with total 1, one part slot, one bit-array entry, count 0, byteSize 0, and the original hash. Tests were added for memory-limit behavior around valid, boundary, excessive, and very large Total values.

# Why It Matters

1. Limits resource pressure from oversized block-part counts.

2. Prevents over-limit proposal metadata from entering ProposalBlockParts setup.

3. Avoids peer proposal-state updates for proposals with excessive part counts.

4. Adds defense in depth for direct PartSet construction.

# Evidence Notes

Grounded evidence is limited to oversized PartSetHeader.Total handling in sei-tendermint/types/part_set.go, sei-tendermint/internal/consensus/state.go, sei-tendermint/internal/consensus/peer_state.go, and related memory-limit tests. The draft's resource-exhaustion framing is supported. Claims about replay, signature validation bypass, cryptographic failure, unauthenticated exploitability, or proven consensus safety failure are not supported by the provided evidence. Confidence is medium rather than high because the exact allocation impact and attacker reachability are not fully demonstrated in the supplied snippets. Protocol security invariant: Consensus proposal PartSetHeader.Total should not exceed MaxBlockPartsCount before it is used to initialize block-part tracking state or update peer/proposal state. Verification notes: Does not prove a signature bypass or replay vulnerability. Does not prove consensus safety failure beyond resource pressure from oversized part counts. Does not prove exploitability by unauthenticated peers; the evidence only shows consensus proposal/peer-state handling of oversized Total values. Does not show the full memory impact size, only that allocation/control state was previously derived from header.Total without this bound. No external verification was performed; assessment is based only on the provided input. Supported classification is resource-exhaustion, not replay-or-signature-validation. Keep in corpus as a likely security fix because the patch enforces resource bounds in consensus proposal handling. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `availability, resource-exhaustion`
Final tags: `infrastructure, consensus, resource-exhaustion, memory-limit, bounds-check, input-validation`

The provided patch clearly adds bounds checks for externally influenced consensus proposal PartSetHeader.Total values before they drive PartSet or peer/proposal state behavior, and tests describe memory-limit coverage. This supports retaining the case as security hardening for resource-exhaustion risk in consensus handling. The evidence does not prove a concrete exploitable vulnerability, unauthenticated remote DoS, cryptographic failure, replay issue, or signature bypass, so security-fix and cryptography/signature framing are too strong.

## Security Evidence

1. NewPartSetFromHeader now guards header.Total against MaxBlockPartsCount and avoids constructing normal arrays from excessive values.
2. defaultSetProposal now rejects proposals whose BlockID.PartSetHeader.Total exceeds MaxBlockPartsCount with ErrInvalidProposalPartSetHeader.
3. PeerState.SetHasProposal now returns early for nil proposals and proposals with excessive PartSetHeader.Total before state mutation.
4. Added tests explicitly cover proposals exceeding memory limits and very large Total values.

## Missing Evidence

1. No proof of unauthenticated attacker reachability is provided.
2. No concrete crash, OOM, allocation size, or exploit trace is shown.
3. No evidence supports cryptographic, replay, signature-validation, or consensus-safety claims beyond resource pressure.
4. The patch evidence does not show whether all call paths receiving untrusted PartSetHeader.Total are covered.

## Claim Boundaries

1. Classify as consensus resource-bound hardening, not a proven vulnerability fix.
2. Do not claim signature bypass, replay attack, or cryptographic weakness.
3. Do not claim confirmed remote DoS without stronger reachability and impact evidence.
4. Keep impact limited to availability/resource-exhaustion risk from excessive block-part counts.
