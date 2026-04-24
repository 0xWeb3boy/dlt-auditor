---
case_id: case_20260212_f45028f01
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2026-02-12
source_refs:
  - git:f45028f01ac837ce8b6bce4c55246ceee08d8258
  - "sei-tendermint/internal/consensus/state.go:2108"
  - "sei-tendermint/internal/consensus/state.go:2243"
  - "sei-tendermint/internal/consensus/state.go:1418"
  - "sei-tendermint/internal/consensus/state.go:1795"
bug_class: consensus-state-mismatch
impact_type:
  - consensus-liveness
  - node-halt
confidence: medium
tags:
  - consensus
  - validator
  - proposal-validation
  - commit-certificate
  - liveness
  - state-consistency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a Tendermint consensus liveness/state-alignment fix for a halt described as caused by reconstructing a block from a bad proposal. It adds a commit-certificate-aware proposal mismatch check, centralizes proposal block reconstruction around current round state, avoids reconstructing over an existing ProposalBlock, and makes commit handling wait for block parts matching the certified PartSetHeader. The evidence does not establish attacker control, threshold assumptions, remote exploitability, or a consensus safety violation, so it should not be retained as a confirmed security fix.

## Observed Patch Facts

1. In `sei-tendermint/internal/consensus/state.go`, the patch replaces `// Verify POLRound, which must be -1 or in range [0, proposal.Round).` with `// If we already know the commit block for this height, ignore proposals that don't m...`.

2. In `sei-tendermint/internal/consensus/state.go`, the patch replaces `func (cs *State) tryCreateProposalBlock(ctx context.Context, height int64, round int3...` with `func (cs *State) tryCreateProposalBlock(ctx context.Context) bool {`.

3. In `sei-tendermint/internal/consensus/state.go`, the patch replaces `if cs.config.GossipTransactionKeyOnly {` with `// Attempt to reconstruct block, in case more transactions have arrived to mempool.`.

4. In `sei-tendermint/internal/consensus/state.go`, the patch replaces `if !cs.roundState.ProposalBlock().HashesTo(blockID.Hash) {` with `if !cs.roundState.ProposalBlockParts().HasHeader(blockID.PartSetHeader) {`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/consensus`, `sei-tendermint/internal`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `sei-tendermint/internal/consensus/state_test.go`, `sei-tendermint/internal/consensus/replay_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/consensus/state_test.go`, `sei-tendermint/internal/consensus/replay_test.go`. The strongest project-level identifiers around this patch are `roundState`, `block`, `blockID`, and `proposal`. Nearby tests or test-like files include `sei-tendermint/internal/test/factory/block.go`, `sei-tendermint/internal/state/test/factory/block.go`.

## Before/After Behavior

Before the patch, defaultSetProposal moved from height/round checks into normal proposal validation without checking whether the node was already in RoundStepCommit with a +2/3 precommit certificate for a different BlockID. After the patch, during commit step it compares proposal.BlockID with the certified blockID and ignores mismatches. Before the patch, proposal block reconstruction accepted explicit construction inputs and the GossipTransactionKeyOnly prevote path included inline reconstruction logic. After the patch, tryCreateProposalBlock derives from roundState, returns if ProposalBlock already exists, and defaultDoPrevote calls it before nil-prevote handling. Before the patch, enterCommit checked the current ProposalBlock hash against the commit hash. After the patch, it checks whether ProposalBlockParts has the committed blockID.PartSetHeader and waits for the committed block parts when needed.

# Root Cause

The supported root cause is inconsistent or stale proposal block state during commit handling: a node could have commit-step evidence for one BlockID while proposal or reconstruction paths still considered data associated with another proposal. The patch treats the commit certificate's BlockID and PartSetHeader as authoritative in these paths. The evidence does not prove this was exploitable by an adversary or that it caused a safety failure.

## Walkthrough

1. A node can enter commit step with Precommits(commitRound).TwoThirdsMajority() returning a non-nil blockID.

2. The patched defaultSetProposal now ignores a same-height, same-round proposal if its proposal.BlockID differs from that certified blockID during RoundStepCommit.

3. The patched tryCreateProposalBlock uses current roundState and skips work when ProposalBlock already exists, reducing opportunities to rebuild over established proposal block state.

4. defaultDoPrevote now invokes tryCreateProposalBlock before deciding whether ProposalBlock is nil and whether to prevote nil.

5. enterCommit now checks ProposalBlockParts().HasHeader(blockID.PartSetHeader) and waits for the committed block parts when the current parts do not match.

6. The resulting behavior keeps proposal block data aligned with the commit certificate, addressing the halt scenario described by the commit subject.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/consensus/state.go | 2098 | defaultSetProposal rejects proposals whose BlockID conflicts with an existing +2/3 precommit certificate during commit step |
| sei-tendermint/internal/consensus/state.go | 2226 | getBlockFromBlockParts and tryCreateProposalBlock reconstruct ProposalBlock from received block parts and current round state |
| sei-tendermint/internal/consensus/state.go | 1405 | defaultDoPrevote attempts proposal block reconstruction before deciding whether to prevote nil |
| sei-tendermint/internal/consensus/state.go | 1756 | enterCommit aligns ProposalBlockParts with the certified commit BlockID and waits for the committed block when needed |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/consensus/state.go:2108` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// Verify POLRound, which must be -1 or in range [0, proposal.Round).
	if proposal.POLRound < -1 ||
```
After
```go
}

	// If we already know the commit block for this height, ignore proposals that don't match it.
	if commitRound := cs.roundState.CommitRound(); commitRound >= 0 && cs.roundState.Step() == cstypes.RoundStepCommit {
		blockID, ok := cs.roundState.Votes().Precommits(commitRound).TwoThirdsMajority()
		if ok && !blockID.IsNil() && !proposal.BlockID.Equals(blockID) {
			cs.logger.Debug(
				"ignoring proposal that mismatches commit certificate",
```

## Snippet 2

Context: `sei-tendermint/internal/consensus/state.go:2243` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (cs *State) tryCreateProposalBlock(ctx context.Context, height int64, round int32, header types.Header, lastCommit *types.Commit, evidence []types.Evidence, proposerAddress types.Address) bool {
	_, span := cs.tracer.Start(ctx, "cs.state.tryCreateProposalBlock")
	span.SetAttributes(attribute.Int("round", int(round)))
	defer span.End()

	// Blocks might be reused, so round mismatch is OK
```
After
```go
}

func (cs *State) tryCreateProposalBlock(ctx context.Context) bool {
	if cs.roundState.ProposalBlock() != nil {
		// Block already constructed.
		return false
	}
	defer func() {
```

## Snippet 3

Context: `sei-tendermint/internal/consensus/state.go:1418` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	if cs.config.GossipTransactionKeyOnly {
		if cs.roundState.ProposalBlock() == nil {
			// If we're not the proposer, we need to build the block
			txKeys := cs.roundState.Proposal().TxKeys
			if cs.roundState.ProposalBlockParts().IsComplete() {
				block, err := cs.getBlockFromBlockParts()
```
After
```go
}

	// Attempt to reconstruct block, in case more transactions have arrived to mempool.
	cs.tryCreateProposalBlock(ctx)

	if cs.roundState.ProposalBlock() == nil {
		logger.Error("prevote step: ProposalBlock is nil")
		cs.signAddVote(ctx, tmproto.PrevoteType, nil, types.PartSetHeader{})
```

## Snippet 4

Context: `sei-tendermint/internal/consensus/state.go:1795` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
if cs.roundState.LockedBlock().HashesTo(blockID.Hash) {
		logger.Info("commit is for a locked block; set ProposalBlock=LockedBlock", "block_hash", blockID.Hash)
		cs.roundState.SetProposalBlock(cs.roundState.LockedBlock())
		cs.roundState.SetProposalBlockParts(cs.roundState.LockedBlockParts())
	}

	// If we don't have the block being committed, set up to get it.
	if !cs.roundState.ProposalBlock().HashesTo(blockID.Hash) {
```
After
```go
if cs.roundState.LockedBlock().HashesTo(blockID.Hash) {
		logger.Info("commit is for a locked block; set ProposalBlock=LockedBlock", "block_hash", blockID.Hash)
		cs.roundState.SetProposalBlockParts(cs.roundState.LockedBlockParts())
		cs.roundState.SetProposalBlock(cs.roundState.LockedBlock())
	}

	// If we don't have the block being committed, set up to get it.
	if !cs.roundState.ProposalBlockParts().HasHeader(blockID.PartSetHeader) {
```

# Fix Pattern

Anchor commit-step proposal handling and block reconstruction to the certified commit BlockID, ignore conflicting proposals, avoid rebuilding over existing proposal block state, and fetch block parts for the certified PartSetHeader.

## How It Was Fixed

The patch adds a guard in defaultSetProposal that checks CommitRound(), RoundStepCommit, and the +2/3 precommit BlockID before accepting a proposal. It refactors tryCreateProposalBlock to derive from current roundState and no-op when ProposalBlock already exists. It moves prevote-time reconstruction through that helper. It changes enterCommit to compare available ProposalBlockParts against blockID.PartSetHeader and continue waiting when the committed block parts are not present.

# Why It Matters

1. Addresses a consensus halt/liveness failure mode named by the commit subject.

2. Keeps commit-step ProposalBlock and ProposalBlockParts aligned with the +2/3 precommit certificate.

3. Reduces risk that a bad or mismatching proposal affects commit-step state.

4. Does not prove remote exploitability, Byzantine-threshold triggerability, double-spend, double-signing, or signature forgery.

# Evidence Notes

Primary evidence is limited to sei-tendermint/internal/consensus/state.go changes in defaultSetProposal, tryCreateProposalBlock, defaultDoPrevote, and enterCommit. The heuristic baseline's RPC/client serialization interpretation is unsupported by the shown diff and should be discarded. The mapper's Tendermint consensus subsystem is supported. However, classifying this as a security fix is stronger than the evidence allows because the input does not establish an adversarial trigger or concrete security impact beyond liveness/halt behavior. Protocol security invariant: Once a node is in commit step with a non-nil +2/3 precommit BlockID for a height, proposal and block-part handling should remain aligned with that certified BlockID rather than a later or mismatching proposal. The provided evidence supports a consensus state-alignment and liveness invariant, but not a proven security vulnerability. Verification notes: The patch does not prove remote unauthenticated exploitability. The patch does not prove a double-signing, double-spend, or consensus safety violation. The patch does not prove that fewer than Byzantine-threshold validators can trigger the halt. The patch does not show cryptographic signature forgery or hash collision behavior. The patch is not an RPC/client API serialization fix despite the heuristic baseline suggesting that subsystem. No evidence of cryptographic signature forgery or hash collision behavior. No evidence of double-spend, double-signing, or consensus safety break. No evidence that fewer-than-threshold Byzantine validators can trigger the halt. No evidence of remote unauthenticated exploitability. Tests are mentioned only as touched files; no specific test assertions are provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-mismatch`
Final impact type: `consensus-liveness, node-halt`
Final confidence: `medium`
Final tags: `consensus, validator, proposal-validation, commit-certificate, liveness, state-consistency`

The supplied patch evidence supports a conservative security-hardening classification, not a confirmed security fix. The change is in Tendermint consensus code and adds guards that keep proposal and block-part handling aligned with a +2/3 precommit commit certificate, including ignoring proposals whose BlockID conflicts with the certified commit BlockID. The commit subject names a halt caused by reconstructing a block from a bad proposal, which is security-relevant availability/liveness hardening in validator consensus code, but the evidence does not prove exploitability, adversary requirements, or a concrete consensus safety break.

## Security Evidence

1. Consensus code now ignores proposals that mismatch an existing commit certificate during RoundStepCommit.
2. Commit handling now checks ProposalBlockParts against the certified blockID.PartSetHeader instead of only the proposal block hash.
3. Proposal block reconstruction now avoids rebuilding over an existing ProposalBlock and derives from current round state.
4. Commit subject explicitly describes a halt caused by reconstructing a block from a bad proposal.

## Missing Evidence

1. No proof that an unauthenticated remote attacker or sub-threshold Byzantine validator can trigger the halt.
2. No test assertion or incident detail showing exploitability or network-wide impact.
3. No evidence of double-signing, double-spend, signature forgery, or consensus safety violation.
4. No concrete attacker-controlled input path is shown beyond consensus proposal/block handling.

## Claim Boundaries

1. Classify as consensus liveness hardening, not an RPC client API or serialization issue.
2. Do not claim a confirmed exploitable vulnerability from the patch alone.
3. Do not claim consensus safety failure, double-spend, or cryptographic compromise.
4. Do not claim unauthenticated remote denial of service without additional evidence.
