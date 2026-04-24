---
case_id: case_20251113_f6d7875ab
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: p2p-networking
confidence: medium
source_quality: high
date: 2025-11-13
source_refs:
  - git:f6d7875ab046c006e6dede6f0fe33ec4bcbc61ef
  - "sei-tendermint/internal/blocksync/reactor.go:270"
  - "sei-tendermint/internal/consensus/reactor.go:1243"
  - "sei-tendermint/internal/statesync/reactor.go:590"
  - "sei-tendermint/internal/consensus/reactor.go:1294"
bug_class: p2p-invalid-peer-accountability
impact_type:
  - protocol-abuse-mitigation
  - peer-isolation
tags:
  - infrastructure
  - p2p-networking
  - consensus
  - statesync
  - peer-eviction
  - invalid-message-handling
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is security hardening in p2p reactor error handling. The visible patch replaces several passive error-reporting paths with peer eviction in blocksync, consensus state, consensus vote-set-bits, and statesync invalid light-block handling. The evidence supports improved peer accountability for invalid input, but does not establish a concrete exploit, consensus safety failure, privilege escalation, or sustained resource-exhaustion vulnerability.

## Observed Patch Facts

1. In `sei-tendermint/internal/blocksync/reactor.go`, the patch replaces `for {` with `for ctx.Err() == nil {`.

2. In `sei-tendermint/internal/consensus/reactor.go`, the patch replaces `if err := r.handleStateMessage(m); err != nil {` with `if err := r.handleStateMessage(m); err != nil && ctx.Err() == nil {`.

3. In `sei-tendermint/internal/statesync/reactor.go`, the patch replaces `r.sendBlockError(p2p.PeerError{` with `r.evict(resp.peer, fmt.Errorf("statesync: received invalid light block. Expected hash...`.

4. In `sei-tendermint/internal/consensus/reactor.go`, the patch replaces `if err := r.handleVoteSetBitsMessage(m); err != nil {` with `if err := r.handleVoteSetBitsMessage(m); err != nil && ctx.Err() == nil {`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/blocksync`, `sei-tendermint/internal`, `sei-tendermint/internal/consensus`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `sei-tendermint/internal/statesync/block_queue.go`, `sei-tendermint/internal/consensus/reactor_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/consensus/reactor_test.go`, `sei-tendermint/internal/blocksync/pool.go`. The strongest project-level identifiers around this patch are `router`, `From`, `block`, and `blockSyncCh`. Nearby tests or test-like files include `sei-tendermint/internal/consensus/wal_fuzz.go`, `sei-tendermint/internal/test/factory/block.go`.

## Before/After Behavior

Before the patch, visible reactor paths generally logged or sent PeerError/sendBlockError when message handling failed or when statesync received a light block whose hash did not match the trusted LastBlockID. After the patch, active-context handler errors in the shown blocksync and consensus paths call router.Evict, and the invalid statesync light-block response calls r.evict before retrying the height. The blocksync loop and handler-error paths also add ctx.Err() checks so shutdown/cancellation is not treated as peer misconduct.

# Root Cause

The prior behavior did not consistently evict peers associated with protocol handler failures or invalid state-sync block data. In the shown paths, errors tied to m.From or resp.peer could be reported without disconnecting the peer. The patch indicates a peer-discipline gap rather than a proven consensus or cryptographic vulnerability.

## Walkthrough

1. Blocksync receives messages from blockSyncCh and dispatches them through handleMessage.

2. The patched blocksync loop runs while ctx.Err() == nil and evicts m.From on handler error when the context is still active.

3. Consensus state-channel processing now evicts m.From on active-context handleStateMessage errors instead of only logging and sending a peer error.

4. Consensus vote-set-bits processing now applies the same eviction pattern for handleVoteSetBitsMessage errors.

5. Statesync backfill compares a received light block hash with the trusted LastBlockID hash.

6. If the hashes do not match, the patched code evicts resp.peer with statesync-specific context and retries the height.

7. The ctx.Err() guards separate local cancellation or shutdown from peer-attributable failures.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/blocksync/reactor.go | 270 | Blocksync message loop now avoids processing after context cancellation and evicts peers on handler errors while active. |
| sei-tendermint/internal/consensus/reactor.go | 1243 | Consensus state channel handler errors now evict the sending peer instead of only sending a peer error. |
| sei-tendermint/internal/consensus/reactor.go | 1294 | Consensus vote-set-bits channel handler errors now evict the sending peer instead of only sending a peer error. |
| sei-tendermint/internal/statesync/reactor.go | 590 | State sync backfill now evicts a peer that supplies a light block whose hash does not match the trusted LastBlockID. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/blocksync/reactor.go:270` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// gracefully.
func (r *Reactor) processBlockSyncCh(ctx context.Context, blockSyncCh *p2p.Channel) {
	for {
		m, err := blockSyncCh.Recv(ctx)
		if err != nil {
			return
		}
		if err := r.handleMessage(m, blockSyncCh); err != nil {
```
After
```go
// gracefully.
func (r *Reactor) processBlockSyncCh(ctx context.Context, blockSyncCh *p2p.Channel) {
	for ctx.Err() == nil {
		m, err := blockSyncCh.Recv(ctx)
		if err != nil {
			return
		}
		if err := r.handleMessage(m, blockSyncCh); err != nil && ctx.Err() == nil {
```

## Snippet 2

Context: `sei-tendermint/internal/consensus/reactor.go:1243` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return
		}
		if err := r.handleStateMessage(m); err != nil {
			r.logger.Error("failed to process stateCh message", "err", err)
			if ctx.Err() == nil {
				r.router.SendError(p2p.PeerError{NodeID: m.From, Err: err})
			}
		}
```
After
```go
return
		}
		if err := r.handleStateMessage(m); err != nil && ctx.Err() == nil {
			r.router.Evict(m.From, fmt.Errorf("consensus.state: %w", err))
		}
	}
```

## Snippet 3

Context: `sei-tendermint/internal/statesync/reactor.go:590` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
r.logger.Info("received invalid light block. header hash doesn't match trusted LastBlockID",
					"trustedHash", w, "receivedHash", g, "height", resp.block.Height)
				r.sendBlockError(p2p.PeerError{
					NodeID: resp.peer,
					Err:    fmt.Errorf("received invalid light block. Expected hash %v, got: %v", w, g),
				})
				queue.retry(resp.block.Height)
				continue
```
After
```go
r.logger.Info("received invalid light block. header hash doesn't match trusted LastBlockID",
					"trustedHash", w, "receivedHash", g, "height", resp.block.Height)
				r.evict(resp.peer, fmt.Errorf("statesync: received invalid light block. Expected hash %v, got: %v", w, g))
				queue.retry(resp.block.Height)
				continue
```

## Snippet 4

Context: `sei-tendermint/internal/consensus/reactor.go:1294` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return
		}
		if err := r.handleVoteSetBitsMessage(m); err != nil {
			r.logger.Error("failed to process voteSetCh message", "err", err)
			if ctx.Err() == nil {
				r.router.SendError(p2p.PeerError{NodeID: m.From, Err: err})
			}
		}
```
After
```go
return
		}
		if err := r.handleVoteSetBitsMessage(m); err != nil && ctx.Err() == nil {
			r.router.Evict(m.From, fmt.Errorf("consensus.voteSet: %w", err))
		}
	}
```

# Fix Pattern

Replace passive peer-error reporting with active peer eviction for selected p2p handler failures and invalid state-sync block data, guarded by context checks.

## How It Was Fixed

The patch changes visible SendError/sendBlockError paths to router.Evict or r.evict, wraps eviction reasons with subsystem labels, and adds ctx.Err() conditions around loops or eviction decisions to avoid evicting peers during local shutdown.

# Why It Matters

1. Invalid peer responses are less likely to be tolerated indefinitely.

2. Consensus-adjacent p2p handlers apply stricter peer accountability.

3. State sync evicts a peer that serves a light block inconsistent with trusted state.

4. The patch distinguishes local shutdown from peer-originated failure.

5. The evidence supports hardening, not a demonstrated exploitable vulnerability.

# Evidence Notes

Grounded evidence comes from sei-tendermint/internal/blocksync/reactor.go processBlockSyncCh, sei-tendermint/internal/consensus/reactor.go processStateCh and processVoteSetBitsCh, and sei-tendermint/internal/statesync/reactor.go backfill verification. Claims about serialization, canonical state representation, remote code execution, privilege escalation, economic impact, or a proven consensus safety break are unsupported by the provided snippets. Protocol security invariant: P2P reactors should not continue treating peers that send invalid protocol data or state-invalid block data as normal peers; peer-originated handler failures should be attributable to the sender, while local context cancellation or shutdown should not be counted as peer fault. Verification notes: The patch does not prove a consensus safety violation. The patch does not prove remote code execution or privilege escalation. The patch does not show an economic exploit path. The patch does not prove malformed peers could cause sustained resource exhaustion at scale. Changed files not represented in the snippets are not independently classified beyond the visible p2p peer-handling pattern. No command execution or external inspection was used. The classification is limited to the provided diff excerpts. Changed files outside the supplied evidence are not independently classified. Confidence is medium because the code behavior is clear, but the security impact is hardening rather than a proven vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `p2p-invalid-peer-accountability`
Final impact type: `protocol-abuse-mitigation, peer-isolation`
Final tags: `infrastructure, p2p-networking, consensus, statesync, peer-eviction, invalid-message-handling, security-hardening`

The supplied patch evidence supports security hardening, not a concrete security fix. Multiple p2p and consensus-adjacent reactors changed from passive error reporting/logging to evicting peers that cause handler errors or provide an invalid state-sync light block, with context-cancellation guards to avoid misattributing local shutdown as peer misconduct. The original serialization/state-representation framing and client-view-divergence impact are too specific for the visible evidence.

## Security Evidence

1. Consensus state-channel handler errors now call router.Evict for the sending peer while the context is active.
2. Consensus vote-set-bits handler errors now evict the sending peer instead of only sending a peer error.
3. State sync now evicts a peer that returns a light block whose hash does not match the trusted LastBlockID.
4. Blocksync adds active-context guards and changes handler-error handling toward peer eviction.

## Missing Evidence

1. No commit message or patch evidence states a vulnerability, exploit, advisory, or attack scenario.
2. No evidence proves consensus safety failure, client-view divergence, or state inconsistency occurred before the patch.
3. No evidence shows sustained denial of service, resource exhaustion, privilege escalation, or remote code execution.
4. Test evidence is listed but not shown in enough detail to prove a regression for a specific security bug.

## Claim Boundaries

1. Supported as p2p peer-accountability hardening for invalid or erroneous protocol behavior.
2. Do not claim a proven consensus vulnerability or cryptographic verification bypass.
3. Do not classify as serialization or canonical state representation based on the provided snippets.
4. Do not infer exploitability beyond stricter eviction of peers associated with invalid inputs or handler failures.
