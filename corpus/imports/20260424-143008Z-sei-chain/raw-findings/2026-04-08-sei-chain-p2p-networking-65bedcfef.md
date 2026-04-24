---
case_id: case_20260408_65bedcfef
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2026-04-08
source_refs:
  - git:65bedcfef99da9928798d467326e5f677ed148a0
  - "sei-tendermint/internal/mempool/reactor_test.go:204"
  - "sei-tendermint/internal/mempool/reactor.go:171"
  - "sei-tendermint/internal/mempool/mempool.go:416"
  - "sei-tendermint/internal/state/execution.go:451"
bug_class: p2p-peer-abuse-accounting-hardening
impact_type:
  - peer-abuse-mitigation
  - liveness
confidence: medium
tags:
  - infrastructure
  - p2p-networking
  - mempool
  - peer-eviction
  - anti-abuse
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a refactor and lifecycle correction for mempool CheckTx failure accounting: peer penalty state was moved from TxMempool into the mempool Reactor, and the commit message says failure-counter entries were previously never cleaned up. This may be security-relevant as p2p anti-abuse hardening, but the supplied evidence does not establish a concrete vulnerability, exploit path, consensus failure, crash, or externally triggerable denial of service.

## Observed Patch Facts

1. In `sei-tendermint/internal/mempool/reactor_test.go`, the patch replaces `// regression test for https://github.com/tendermint/tendermint/issues/5408` with `func peerFailedCheckTxCount(reactor *Reactor, nodeID types.NodeID) utils.Option[int] {`.

2. In `sei-tendermint/internal/mempool/reactor.go`, the patch replaces `// handleMessage handles an Envelope sent from a peer on a specific p2p Channel.` with `func (r *Reactor) accountFailedCheckTx(nodeID types.NodeID, err error) {`.

3. In `sei-tendermint/internal/mempool/mempool.go`, the patch replaces `func (txmp *TxMempool) incrementBlacklistCounter(nodeID types.NodeID) {` with `func (txmp *TxMempool) isInMempool(tx types.Tx) bool {`.

4. In `sei-tendermint/internal/state/execution.go`, the patch replaces `func (blockExec *BlockExecutor) CheckTxFromPeerProposal(ctx context.Context, tx types...` with `func buildLastCommitInfo(block *types.Block, store Store, initialHeight int64) abci.C...`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/mempool`, `sei-tendermint/internal`, `sei-tendermint/internal/state`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `sei-tendermint/internal/mempool/types.go`, `sei-tendermint/internal/mempool/tx.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/statesync/reactor_test.go`, `sei-tendermint/internal/mempool/tx.go`. The strongest project-level identifiers around this patch are `nodeID`, `types`, `txmp`, and `counts`. Nearby tests or test-like files include `sei-tendermint/internal/test/factory/vote.go`, `sei-tendermint/internal/test/factory/p2p.go`.

## Before/After Behavior

Before the patch, the supplied mempool evidence shows TxMempool.incrementBlacklistCounter owning blacklist accounting: it checked CheckTxErrorBlacklistEnabled, required a nonempty nodeID and router, incremented failedCheckTxCounts[nodeID], and evicted through txmp.router.Evict once the threshold was exceeded. After the patch, the supplied reactor evidence shows handleMempoolMessage calling r.mempool.CheckTx for gossiped transactions and then calling r.accountFailedCheckTx(m.From, err). accountFailedCheckTx gates on CheckTxErrorBlacklistEnabled, filters to ErrTxTooLarge and ErrPreCheck, and increments an existing reactor-owned counter entry for the nodeID. The test evidence adds helpers and a named regression path around failed CheckTx counts and peer eviction, while the commit body states that failure-counter entries were never cleaned up previously.

# Root Cause

The grounded issue is misplaced or incomplete ownership of peer failure-counter state. The old accounting lived in generic TxMempool code even though sender identity and peer lifecycle belong to the p2p reactor. The stale-counter lifecycle issue is supported by the commit body, but the exact harmful behavior caused by stale entries is not shown in the provided hunks.

## Walkthrough

1. A p2p peer sends a mempool Txs message handled by handleMempoolMessage in the mempool reactor.

2. The reactor validates the message, derives TxInfo from the peer, and calls mempool.CheckTx for each transaction.

3. When CheckTx returns an error, the patched reactor calls accountFailedCheckTx with m.From and the error.

4. accountFailedCheckTx returns unless blacklist accounting is enabled and the error is ErrTxTooLarge or ErrPreCheck.

5. For eligible errors, the reactor updates failedCheckTxCounts for an existing nodeID entry.

6. Before the patch, the comparable counter increment and eviction helper lived in TxMempool.incrementBlacklistCounter.

7. Tests were updated to inspect reactor failure counts and cover the moved peer-accounting behavior.

8. The commit message separately states that failure-counter entries previously were never cleaned up.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/mempool/reactor.go | 125 | p2p mempool message handling path that validates gossiped transactions and attributes CheckTx failures to the sending peer |
| sei-tendermint/internal/mempool/reactor.go | 171 | reactor-owned failed CheckTx accounting and threshold-based peer penalty logic |
| sei-tendermint/internal/mempool/mempool.go | 416 | old mempool-owned blacklist counter and eviction logic removed from generic CheckTx handling |
| sei-tendermint/internal/mempool/reactor_test.go | 204 | regression coverage for failed CheckTx count tracking, peer eviction, and counter lifecycle cleanup |
| sei-tendermint/internal/state/execution.go | 451 | consensus proposal CheckTx caller that should not be treated as an ordinary p2p peer for eviction accounting |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/mempool/reactor_test.go:204` (changes a sensitive control or state-update path)

Before
```go
}

// regression test for https://github.com/tendermint/tendermint/issues/5408
func TestReactorConcurrency(t *testing.T) {
```
After
```go
}

func peerFailedCheckTxCount(reactor *Reactor, nodeID types.NodeID) utils.Option[int] {
	for counts := range reactor.failedCheckTxCounts.Lock() {
		if count, ok := counts[nodeID]; ok {
			return utils.Some(count)
		}
		return utils.None[int]()
```

## Snippet 2

Context: `sei-tendermint/internal/mempool/reactor.go:171` (changes an authorization or privilege gate)

Before
```go
}

// handleMessage handles an Envelope sent from a peer on a specific p2p Channel.
// It will handle errors and any possible panics gracefully. A caller can handle
```
After
```go
}

func (r *Reactor) accountFailedCheckTx(nodeID types.NodeID, err error) {
	if !r.cfg.CheckTxErrorBlacklistEnabled {
		return
	}
	if !utils.ErrorAs[types.ErrTxTooLarge](err).IsPresent() && !utils.ErrorAs[types.ErrPreCheck](err).IsPresent() {
		return
```

## Snippet 3

Context: `sei-tendermint/internal/mempool/mempool.go:416` (changes an authorization or privilege gate)

Before
```go
}

func (txmp *TxMempool) incrementBlacklistCounter(nodeID types.NodeID) {
	if !txmp.config.CheckTxErrorBlacklistEnabled || nodeID == "" || txmp.router == nil {
		return
	}

	for counts := range txmp.failedCheckTxCounts.Lock() {
```
After
```go
}

func (txmp *TxMempool) isInMempool(tx types.Tx) bool {
	existingTx := txmp.txStore.GetTxByHash(tx.Key())
```

## Snippet 4

Context: `sei-tendermint/internal/state/execution.go:451` (changes a sensitive control or state-update path)

Before
```go
}

func (blockExec *BlockExecutor) CheckTxFromPeerProposal(ctx context.Context, tx types.Tx) {
	// Ignore errors from CheckTx because there could be benign errors due to the same tx being
	// inserted into the mempool from gossiping. Since such simultaneous insertion could result in
	// multiple different kinds of errors, we will ignore them all here, and verify in the consensus
	// state machine whether all txs in the proposal are present in the mempool at a later time.
	if err := blockExec.mempool.CheckTx(ctx, tx, func(rct *abci.ResponseCheckTx) {}, mempool.TxInfo{
```
After
```go
}

func buildLastCommitInfo(block *types.Block, store Store, initialHeight int64) abci.CommitInfo {
	if block.Height == initialHeight {
```

# Fix Pattern

Move peer failure accounting from generic mempool validation code into the p2p reactor, where peer identity and lifecycle are available. Filter counted failures to selected CheckTx error classes and add regression coverage for counter behavior and cleanup.

## How It Was Fixed

The old TxMempool.incrementBlacklistCounter path shown in mempool.go was removed from that location. The reactor path now attributes CheckTx failures from p2p mempool messages to m.From through accountFailedCheckTx. The new helper checks configuration, limits accounting to ErrTxTooLarge and ErrPreCheck, and updates reactor-owned failedCheckTxCounts. Tests were added around reading peer failure counts and eviction/count lifecycle behavior.

# Why It Matters

1. Keeps peer penalty accounting closer to the p2p layer that knows sender identity.

2. Reduces risk that non-peer CheckTx callers are treated like ordinary p2p peers.

3. Limits failure counting to specific policy-relevant error classes shown in the patch.

4. Addresses stale failure-counter lifecycle according to the commit message.

5. Does not prove a concrete exploitable vulnerability from the supplied evidence.

# Evidence Notes

Primary support comes from sei-tendermint/internal/mempool/reactor.go, sei-tendermint/internal/mempool/mempool.go, sei-tendermint/internal/mempool/reactor_test.go, and the commit body. Unsupported claims removed: malformed-decoding crash, panic path, consensus safety impact, confirmed remote exploitability, and a proven denial-of-service vulnerability. The evidence shows anti-abuse-related accounting and cleanup, but not enough to classify this as a confirmed security fix. Protocol security invariant: If peer CheckTx failure accounting is used as an anti-abuse control, it should be performed in the p2p reactor path that has sender identity and peer lifecycle context, and it should avoid charging unrelated CheckTx callers as peers. Verification notes: No remote exploitability is proven by the patch evidence. No consensus safety violation is shown. No panic or malformed-decoding crash path is supported by the provided hunks. The evidence supports peer-abuse hardening and lifecycle cleanup, not a confirmed critical vulnerability. The exact pre-patch failure mode for stale counters is not fully shown. No commands or file inspection were performed, per instruction. The supplied hunks show accounting movement and filtering, not a complete exploit scenario. The exact stale-counter failure mode is not demonstrated by the provided evidence. Threshold eviction in the new reactor path is suggested by test naming and mapper context, but not fully visible in the quoted implementation hunk. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `p2p-peer-abuse-accounting-hardening`
Final impact type: `peer-abuse-mitigation, liveness`
Final confidence: `medium`
Final tags: `infrastructure, p2p-networking, mempool, peer-eviction, anti-abuse, security-hardening`

The supplied evidence does not prove a concrete exploitable vulnerability, but it does show a security-relevant hardening change in p2p mempool peer penalty accounting. The patch moves CheckTx failure accounting from generic mempool code into the Reactor path that has peer identity and lifecycle context, filters counted failures to selected error classes, and adds tests around failed CheckTx counts and peer eviction/lifecycle behavior. This is stronger than an unclear reliability-only change, but should not be represented as a confirmed security fix.

## Security Evidence

1. Reactor handles p2p mempool messages and calls accountFailedCheckTx with m.From after CheckTx errors.
2. accountFailedCheckTx is gated by CheckTxErrorBlacklistEnabled and only counts ErrTxTooLarge or ErrPreCheck errors.
3. Old TxMempool blacklist counter and router eviction logic was removed from generic mempool code.
4. Commit body states failure counter entries previously were never cleaned up.
5. Tests add helper and named coverage for failed CheckTx count eviction behavior.

## Missing Evidence

1. No concrete exploit path is shown.
2. No demonstrated remote denial-of-service, consensus safety failure, crash, or privilege bypass is shown.
3. The full new eviction threshold logic is not visible in the supplied implementation hunk.
4. The precise harmful effect of stale failure-counter entries is not demonstrated beyond the commit body.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit claims to p2p mempool peer-abuse accounting and failure-counter lifecycle behavior.
3. Do not claim consensus compromise or proven remote exploitability.
4. Do not claim a specific CVE-style vulnerability from the provided evidence.
