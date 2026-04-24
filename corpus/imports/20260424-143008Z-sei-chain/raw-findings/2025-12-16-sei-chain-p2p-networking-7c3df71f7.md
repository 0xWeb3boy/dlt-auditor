---
case_id: case_20251216_7c3df71f7
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: p2p-networking
confidence: medium
source_quality: high
date: 2025-12-16
source_refs:
  - git:7c3df71f798891346a47a51650267404bf86a8f0
  - "sei-tendermint/internal/mempool/mempool.go:452"
  - "sei-tendermint/internal/mempool/mempool.go:758"
  - "sei-tendermint/internal/mempool/mempool_test.go:1133"
  - "sei-tendermint/config/config.go:877"
bug_class: mempool-peer-resource-abuse-hardening
impact_type:
  - resource-exhaustion
  - peer-abuse-mitigation
tags:
  - blockchain-core
  - mempool
  - p2p-networking
  - peer-blacklisting
  - oversized-transaction
  - resource-exhaustion
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is mempool peer-abuse hardening, not a confirmed vulnerability fix. The patch enables CheckTx error blacklisting by default, narrows the blacklist trigger away from all non-OK ABCI CheckTx results, and adds guarded peer eviction accounting. The evidence supports oversized-transaction blacklisting as the intended scope, but does not prove an exploitable denial-of-service vulnerability or consensus impact.

## Observed Patch Facts

1. In `sei-tendermint/internal/mempool/mempool.go`, the patch replaces `func (txmp *TxMempool) isInMempool(tx types.Tx) bool {` with `func (txmp *TxMempool) incrementBlacklistCounter(nodeID types.NodeID) {`.

2. In `sei-tendermint/internal/mempool/mempool.go`, the patch replaces `if res.Code != abci.CodeTypeOK {` with `return err`.

3. In `sei-tendermint/internal/mempool/mempool_test.go`, the patch replaces `tx := []byte("bad tx")` with `badTx := make([]byte, txmp.config.MaxTxBytes+1)`.

4. In `sei-tendermint/config/config.go`, the patch replaces `CheckTxErrorBlacklistEnabled: false,` with `CheckTxErrorBlacklistEnabled: true,`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/mempool`, `sei-tendermint/internal`, `sei-tendermint/config`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `sei-tendermint/internal/mempool/reactor.go`, `sei-tendermint/config/config_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/mempool/reactor.go`, `sei-tendermint/internal/mempool/tx.go`. The strongest project-level identifiers around this patch are `txmp`, `config`, `CheckTxErrorBlacklistEnabled`, and `require`. Nearby tests or test-like files include `sei-tendermint/internal/test/factory/p2p.go`, `sei-tendermint/internal/test/factory/genesis.go`.

## Before/After Behavior

Before the patch, default mempool config disabled CheckTx error blacklisting and used a threshold of 0. The generic addNewTransaction rejection path incremented failedCheckTxCounts for every non-OK ABCI CheckTx result when that path was enabled. After the patch, defaults enable blacklisting with threshold 50, generic non-OK application CheckTx rejection no longer increments the blacklist counter, and peer counting/eviction is centralized in incrementBlacklistCounter with guards for config enablement, non-empty node ID, and router availability. Tests were changed to exercise a transaction larger than MaxTxBytes and to verify disabled blacklisting does not increment the sender count.

# Root Cause

The previous policy was not suitable as a default peer-eviction defense because its counting site was attached to broad application-level CheckTx rejection rather than a clearly bounded peer-abuse condition. As a result, enabling it by default could penalize peers for ordinary invalid application transactions. The patch narrows the policy before enabling it by default.

## Walkthrough

1. DefaultMempoolConfig changed CheckTxErrorBlacklistEnabled from false to true and CheckTxErrorThreshold from 0 to 50.

2. The old addNewTransaction rejection branch incremented failedCheckTxCounts for txInfo.SenderNodeID on non-OK ABCI CheckTx responses.

3. The patch removes that generic failed-count update from addNewTransaction, so ordinary application-level CheckTx failures are no longer automatically blacklist events.

4. The patch adds incrementBlacklistCounter(nodeID), which exits unless blacklisting is enabled, nodeID is non-empty, and a router is available.

5. When incrementBlacklistCounter runs, it locks failedCheckTxCounts, increments the peer count, and evicts the peer once the count exceeds CheckTxErrorThreshold.

6. The updated test uses a transaction sized MaxTxBytes+1, grounding the intended blacklist case in oversized transaction handling.

7. The provided evidence does not show the exact oversized-transaction call site for incrementBlacklistCounter, so the oversized scope is supported by the commit message and test change rather than fully demonstrated by the snippets.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/mempool/mempool.go | 452 | Adds incrementBlacklistCounter gated by CheckTxErrorBlacklistEnabled, non-empty nodeID, and router availability, then evicts peers exceeding CheckTxErrorThreshold. |
| sei-tendermint/internal/mempool/mempool.go | 740 | Rejected transaction handling no longer increments blacklist counters for every non-OK ABCI CheckTx result, narrowing blacklist behavior to the intended path. |
| sei-tendermint/config/config.go | 866 | Changes default mempool configuration to enable CheckTx error blacklisting with threshold 50. |
| sei-tendermint/internal/mempool/mempool_test.go | 1122 | Updates failed CheckTx count test to use a transaction larger than MaxTxBytes and assert behavior around blacklist enablement. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/mempool/mempool.go:452` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (txmp *TxMempool) isInMempool(tx types.Tx) bool {
	existingTx := txmp.txStore.GetTxByHash(tx.Key())
```
After
```go
}

func (txmp *TxMempool) incrementBlacklistCounter(nodeID types.NodeID) {
	if !txmp.config.CheckTxErrorBlacklistEnabled || nodeID == "" || txmp.router == nil {
		return
	}

	txmp.mtxFailedCheckTxCounts.Lock()
```

## Snippet 2

Context: `sei-tendermint/internal/mempool/mempool.go:758` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
wtx.removeHandler(!txmp.config.KeepInvalidTxsInCache)
		if res.Code != abci.CodeTypeOK {
			txmp.mtxFailedCheckTxCounts.Lock()
			defer txmp.mtxFailedCheckTxCounts.Unlock()
			txmp.failedCheckTxCounts[txInfo.SenderNodeID]++
			if txmp.config.CheckTxErrorBlacklistEnabled && txmp.failedCheckTxCounts[txInfo.SenderNodeID] > uint64(txmp.config.CheckTxErrorThreshold) {
				txmp.router.Evict(txInfo.SenderNodeID, errors.New("mempool: checkTx error exceeded threshold"))
```
After
```go
wtx.removeHandler(!txmp.config.KeepInvalidTxsInCache)

		return err
	}
```

## Snippet 3

Context: `sei-tendermint/internal/mempool/mempool_test.go:1133` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
	txmp := setup(t, client, 0, WithPostCheck(postCheckFn))
	tx := []byte("bad tx")

	callback := func(res *abci.ResponseCheckTx) {
		require.Equal(t, nil, txmp.postCheck(tx, res))
	}
	require.Equal(t, uint64(0), txmp.GetPeerFailedCheckTxCount("sender"))
```
After
```go
}
	txmp := setup(t, client, 0, WithPostCheck(postCheckFn))
	badTx := make([]byte, txmp.config.MaxTxBytes+1)

	callback := func(res *abci.ResponseCheckTx) {
		require.Equal(t, nil, txmp.postCheck(badTx, res))
	}
	require.Equal(t, uint64(0), txmp.GetPeerFailedCheckTxCount("sender"))
```

## Snippet 4

Context: `sei-tendermint/config/config.go:877` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
TTLNumBlocks:                 10,              // remove txs after 10 blocks
		TxNotifyThreshold:            0,
		CheckTxErrorBlacklistEnabled: false,
		CheckTxErrorThreshold:        0,
		PendingSize:                  5000,
		MaxPendingTxsBytes:           1024 * 1024 * 1024, // 1GB
```
After
```go
TTLNumBlocks:                 10,              // remove txs after 10 blocks
		TxNotifyThreshold:            0,
		CheckTxErrorBlacklistEnabled: true,
		CheckTxErrorThreshold:        50,
		PendingSize:                  5000,
		MaxPendingTxsBytes:           1024 * 1024 * 1024, // 1GB
```

# Fix Pattern

Narrow a peer-penalty mechanism to a bounded abuse condition, centralize the counter/eviction logic behind explicit guards, then enable the narrowed defensive control by default.

## How It Was Fixed

The patch added incrementBlacklistCounter in sei-tendermint/internal/mempool/mempool.go, removed failed peer counting from the generic addNewTransaction non-OK CheckTx branch, changed default mempool config to enable blacklisting with threshold 50, and updated the failed-count test to use an oversized transaction.

# Why It Matters

1. Helps bound repeated peer submissions of oversized transactions.

2. Makes the narrowed blacklist defense active under default configuration.

3. Avoids treating every application-level CheckTx failure as grounds for peer eviction.

4. The impact is limited to mempool resource-abuse hardening; consensus safety, authorization, and signature validation are not shown to be affected.

# Evidence Notes

Strong evidence supports a mempool peer blacklisting policy change in sei-tendermint/internal/mempool/mempool.go and default configuration changes in sei-tendermint/config/config.go. The test evidence supports oversized transactions as the intended exercised case. The commit message explicitly says blacklisting is enabled by default and weakened to apply only to oversized transactions. The evidence does not support the heuristic baseline about serialization or canonical state representation. It also does not establish a concrete exploit path, remote DoS severity, consensus failure, or transaction authorization bypass. Protocol security invariant: The mempool should reject transactions larger than MaxTxBytes and, when the configured blacklist policy is active, count repeated oversized transaction submissions from an identified peer toward eviction without treating every generic application-level CheckTx rejection as peer abuse. Verification notes: The patch does not prove a remotely exploitable denial-of-service condition by itself. The patch does not show consensus safety, signature validation, or transaction authorization being fixed. The patch does not establish that all invalid transactions should trigger peer eviction; it explicitly narrows that behavior. The evidence does not support the heuristic baseline claim about canonical serialization or state representation. No commands or external inspection were performed, per instruction. Classification is downgraded from confirmed to likely because the evidence shows hardening intent and policy changes but not a demonstrated vulnerability exploit. Confidence is medium because the snippets do not include the exact oversized-transaction call site for incrementBlacklistCounter. Keep in corpus as security hardening, not as a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-peer-resource-abuse-hardening`
Final impact type: `resource-exhaustion, peer-abuse-mitigation`
Final tags: `blockchain-core, mempool, p2p-networking, peer-blacklisting, oversized-transaction, resource-exhaustion, security-hardening`

The supplied evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The patch enables CheckTx error blacklisting by default, sets a nonzero threshold, centralizes guarded peer eviction accounting, and narrows the policy away from all application CheckTx failures toward oversized transactions. That is a security-relevant abuse-mitigation change in a P2P mempool path, but the evidence does not prove a concrete exploitable denial-of-service or consensus/state-divergence bug.

## Security Evidence

1. Default mempool config changes CheckTxErrorBlacklistEnabled from false to true.
2. Default CheckTxErrorThreshold changes from 0 to 50, making the blacklist policy usable by default.
3. New incrementBlacklistCounter guards on enabled config, non-empty node ID, and router availability before counting and evicting peers.
4. Eviction is triggered when a peer exceeds the configured CheckTx error threshold.
5. Generic non-OK ABCI CheckTx failures no longer increment blacklist counters, reducing overbroad peer punishment.
6. Tests were updated to use a transaction larger than MaxTxBytes, matching the commit message's oversized-transaction scope.

## Missing Evidence

1. No exploit path or demonstrated remote denial-of-service scenario is shown.
2. The supplied snippets do not include the exact oversized-transaction call site invoking incrementBlacklistCounter.
3. No evidence shows consensus safety, state consistency, serialization, authorization, or signature validation impact.
4. No severity evidence shows that the prior default caused practical resource exhaustion.

## Claim Boundaries

1. Classify as mempool peer-abuse hardening, not a proven vulnerability fix.
2. Do not claim state-consistency or client-view-divergence impact from this evidence.
3. Do not claim all invalid transactions are security-relevant blacklist events; the patch narrows away from that behavior.
4. Do not claim consensus or transaction-authentication impact.
