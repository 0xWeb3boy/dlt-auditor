---
case_id: case_20230112_e52126b92
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: high
date: 2023-01-12
source_refs:
  - git:e52126b9235ec51e9496d4ab229e74e4a6c7b089
  - "sei-tendermint/config/config.go:831"
  - "sei-tendermint/internal/mempool/mempool.go:553"
  - "sei-tendermint/config/config.go:775"
  - "sei-tendermint/internal/mempool/mempool_test.go:687"
bug_class: mempool-invalid-tx-peer-abuse-hardening
impact_type:
  - resource-abuse-mitigation
  - liveness
confidence: medium
tags:
  - blockchain-core
  - p2p-networking
  - mempool
  - checktx
  - peer-eviction
  - abuse-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds optional CheckTx-error blacklisting in the mempool: failed CheckTx results are still counted per SenderNodeID, and when the new config flag is enabled and the count exceeds the configured threshold, the peer manager is notified with an error that tests treat as eviction. This may be security-relevant resource-abuse hardening, but the supplied evidence does not establish an exploitable vulnerability, default exposure, resource exhaustion impact, or required attack conditions.

## Observed Patch Facts

1. In `sei-tendermint/config/config.go`, the patch adds `if cfg.CheckTxErrorThreshold < 0 {`.

2. In `sei-tendermint/internal/mempool/mempool.go`, the patch adds `if txmp.config.CheckTxErrorBlacklistEnabled && txmp.failedCheckTxCounts[txInfo.Sender...`.

3. In `sei-tendermint/config/config.go`, the patch adds `// If a peer has sent more transactions failing CheckTx than this threshold,`.

4. In `sei-tendermint/internal/mempool/mempool_test.go`, the patch adds `// enable blacklisting`.

## Project Context

The changed code sits primarily in `sei-tendermint/config`, `sei-tendermint/internal/mempool`, `sei-tendermint/internal`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `sei-tendermint/internal/mempool/reactor.go`, `sei-tendermint/config/toml.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/mempool/reactor.go`, `sei-tendermint/config/toml.go`. The strongest project-level identifiers around this patch are `txmp`, `threshold`, `SenderNodeID`, and `CheckTxErrorThreshold`. Nearby tests or test-like files include `sei-tendermint/internal/test/factory/vote.go`, `sei-tendermint/internal/test/factory/validator.go`.

## Before/After Behavior

Before the patch, the shown CheckTx failure path logged rejected transactions, incremented metrics, optionally removed invalid transactions from cache, and incremented failedCheckTxCounts for the sender when ResponseCheckTx.Code was not OK. No enforcement action after that counter increment is shown. After the patch, the same path checks CheckTxErrorBlacklistEnabled and whether the sender's failed count is greater than CheckTxErrorThreshold, then calls peerManager.Errored for that SenderNodeID. The configuration now exposes the enable flag and threshold, and validation rejects negative thresholds.

# Root Cause

The grounded pre-patch gap is that a per-sender failed CheckTx counter existed but, in the supplied snippets, was not tied to any eviction or peer-management action. The evidence does not prove that this gap was exploitable as a vulnerability; it only supports that the patch added a configurable enforcement policy for repeated CheckTx failures.

## Walkthrough

1. A transaction reaches TxMempool.initTxCallback with TxInfo including SenderNodeID.

2. If post-check fails or ResponseCheckTx.Code is not OK, the transaction is handled as rejected.

3. For non-OK CheckTx responses, failedCheckTxCounts[txInfo.SenderNodeID] is incremented under a mutex.

4. Before the change, the supplied snippet shows no eviction or peer-manager call after the counter increment.

5. After the change, the code checks whether CheckTxErrorBlacklistEnabled is true and whether the failed count exceeds CheckTxErrorThreshold.

6. If both conditions hold, peerManager.Errored is called with the sender node ID and a CheckTx-threshold error.

7. MempoolConfig gains CheckTxErrorBlacklistEnabled and CheckTxErrorThreshold fields.

8. ValidateBasic rejects a negative CheckTxErrorThreshold.

9. The updated test enables blacklisting, sets the threshold to 0, submits a bad transaction, and asserts the test peer evictor marks the sender as evicted.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/mempool/mempool.go | 553 | enforces eviction when a sender's failed CheckTx count exceeds the configured threshold |
| sei-tendermint/config/config.go | 775 | adds mempool configuration fields controlling CheckTx error blacklisting and threshold |
| sei-tendermint/config/config.go | 831 | validates that the CheckTx error threshold is not negative |
| sei-tendermint/internal/mempool/mempool_test.go | 687 | adds regression coverage that a sender is evicted after blacklisting is enabled and the threshold is exceeded |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/config/config.go:831` (changes an authorization or privilege gate)

Before
```go
return errors.New("tx-notify-threshold can't be negative")
	}

	return nil
```
After
```go
return errors.New("tx-notify-threshold can't be negative")
	}
	if cfg.CheckTxErrorThreshold < 0 {
		return errors.New("check-tx-error-threshold can't be negative")
	}

	return nil
```

## Snippet 2

Context: `sei-tendermint/internal/mempool/mempool.go:553` (changes an authorization or privilege gate)

Before
```go
defer txmp.mtxFailedCheckTxCounts.Unlock()
			txmp.failedCheckTxCounts[txInfo.SenderNodeID]++
		}
		return err
```
After
```go
defer txmp.mtxFailedCheckTxCounts.Unlock()
			txmp.failedCheckTxCounts[txInfo.SenderNodeID]++
			if txmp.config.CheckTxErrorBlacklistEnabled && txmp.failedCheckTxCounts[txInfo.SenderNodeID] > uint64(txmp.config.CheckTxErrorThreshold) {
				// evict peer
				txmp.peerManager.Errored(txInfo.SenderNodeID, errors.New("checkTx error exceeded threshold"))
			}
		}
		return err
```

## Snippet 3

Context: `sei-tendermint/config/config.go:775` (changes a sensitive control or state-update path)

Before
```go
// needed to trigger a notification in mempool's Tx notifier
	TxNotifyThreshold int `mapstructure:"tx-notify-threshold"`
}
```
After
```go
// needed to trigger a notification in mempool's Tx notifier
	TxNotifyThreshold int `mapstructure:"tx-notify-threshold"`

	// If a peer has sent more transactions failing CheckTx than this threshold,
	// blacklist the peer.
	CheckTxErrorBlacklistEnabled bool `mapstructure:"check-tx-error-blacklist-enabled"`
	CheckTxErrorThreshold        int  `mapstructure:"check-tx-error-threshold"`
}
```

## Snippet 4

Context: `sei-tendermint/internal/mempool/mempool_test.go:687` (changes a sensitive control or state-update path)

Before
```go
require.NoError(t, txmp.CheckTx(ctx, tx, callback, TxInfo{SenderID: 0, SenderNodeID: "sender"}))
	require.Equal(t, uint64(2), txmp.GetPeerFailedCheckTxCount("sender"))
}
```
After
```go
require.NoError(t, txmp.CheckTx(ctx, tx, callback, TxInfo{SenderID: 0, SenderNodeID: "sender"}))
	require.Equal(t, uint64(2), txmp.GetPeerFailedCheckTxCount("sender"))

	// enable blacklisting
	txmp.config.CheckTxErrorBlacklistEnabled = true
	txmp.config.CheckTxErrorThreshold = 0
	tx = []byte("bad tx")
	require.NoError(t, txmp.CheckTx(ctx, tx, callback, TxInfo{SenderID: 0, SenderNodeID: "sender"}))
```

# Fix Pattern

Add a configurable per-peer threshold to an existing failed-validation counter and invoke peer eviction when the threshold is exceeded, with basic validation for the new threshold setting.

## How It Was Fixed

The patch adds CheckTxErrorBlacklistEnabled and CheckTxErrorThreshold to MempoolConfig, validates that the threshold is not negative, and extends TxMempool.initTxCallback so repeated non-OK CheckTx responses from the same SenderNodeID can trigger peerManager.Errored when blacklisting is enabled. A regression test covers eviction under an enabled flag and zero threshold.

# Why It Matters

1. Adds an enforcement action to an existing per-peer failed CheckTx counter.

2. May reduce repeated invalid-transaction load from a single peer when enabled.

3. Does not prove a concrete exploit, crash, consensus failure, or default-enabled protection.

4. Best treated as potentially security-relevant hardening, not a confirmed vulnerability fix.

# Evidence Notes

Strong evidence supports the code behavior change in internal/mempool/mempool.go, the new config fields and validation in config/config.go, and test coverage in internal/mempool/mempool_test.go. Unsupported claims removed: node crash, panic-prone conversion, malformed decoding, consensus impact, funds loss, privilege escalation, quantified denial of service, and default enablement. Protocol security invariant: The evidence suggests a desired policy that peers repeatedly submitting transactions rejected by CheckTx can be disconnected after a configurable threshold, but the provided patch does not establish that the pre-patch behavior violated a concrete security invariant or enabled a demonstrated denial of service. Verification notes: The patch does not prove a node crash or panic existed before the change. The patch does not show whether CheckTx error blacklisting is enabled by default. The patch does not prove a consensus safety failure, funds loss, or privilege escalation. The patch does not quantify the resources required for a peer to cause harm before eviction. The patch does not show global rate limiting; it only adds per-sender failed-CheckTx eviction behavior. No evidence provided that blacklisting is enabled by default. No evidence provided that repeated failed CheckTx transactions caused resource exhaustion in practice. No evidence provided for crash, panic, consensus safety impact, or economic loss. Test evidence confirms the intended eviction behavior only when the new option is enabled. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-invalid-tx-peer-abuse-hardening`
Final impact type: `resource-abuse-mitigation, liveness`
Final confidence: `medium`
Final tags: `blockchain-core, p2p-networking, mempool, checktx, peer-eviction, abuse-hardening`

The supplied patch clearly adds a configurable enforcement mechanism that evicts or errors peers after repeated failed CheckTx submissions. In a blockchain P2P mempool path, limiting peers that repeatedly submit invalid transactions is security-relevant abuse hardening. The evidence does not prove a concrete exploitable vulnerability, default enablement, quantified denial of service, or consensus impact, so this should not be treated as a confirmed security fix.

## Security Evidence

1. Adds CheckTxErrorBlacklistEnabled and CheckTxErrorThreshold to mempool configuration.
2. Counts failed CheckTx responses per SenderNodeID and calls peerManager.Errored when the enabled threshold is exceeded.
3. Commit subject explicitly describes evicting peer connections for too many failed CheckTx transactions.
4. Regression test enables blacklisting, sets threshold to zero, submits a bad transaction, and asserts the peer is evicted.
5. Threshold validation prevents negative CheckTxErrorThreshold configuration.

## Missing Evidence

1. No proof that blacklisting is enabled by default.
2. No demonstrated exploit, crash, consensus failure, or economic loss.
3. No quantified resource exhaustion or liveness degradation from repeated failed CheckTx submissions.
4. No evidence of attacker prerequisites, network exposure details, or bypass analysis.

## Claim Boundaries

1. Classify as security hardening, not a concrete vulnerability fix.
2. Supported claim is configurable peer eviction for repeated invalid CheckTx results.
3. Do not claim consensus safety impact, funds loss, privilege escalation, panic, or default protection.
4. Do not infer global rate limiting; the patch shows per-sender failed-CheckTx enforcement only.
