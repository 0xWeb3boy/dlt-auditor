---
case_id: case_20250929_09ef1ddb
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-09-29
source_refs:
  - git:09ef1ddb5c6b4b7dd76015ec5c8eacb8f8eb638d
  - "rollup/internal/controller/watcher/l2_watcher.go:112"
  - "rollup/internal/controller/watcher/l2_watcher.go:102"
  - "rollup/internal/controller/watcher/l2_watcher.go:43"
  - "rollup/cmd/rollup_relayer/app/app.go:112"
bug_class: canonical-input-selection
impact_type:
  - hash-integrity
confidence: medium
tags:
  - blockchain-core
  - validium
  - message-queue
  - hashing
  - fail-closed
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a validium-specific correctness fix in how the watcher sources L1 message transactions before later processing. It does not, by itself, establish a vulnerability, exploit path, or concrete security impact, so the strongest justified classification is unclear rather than confirmed security.

## Observed Patch Facts

1. In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `withdrawRoot, err3 := w.StorageAt(ctx, w.messageQueueAddress, w.withdrawTrieRootSlot,...` with `// use original (encrypted) L1 message txs in validium mode`.

2. In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `for _, tx := range block.Transactions() {` with `blockTxs := block.Transactions()`.

3. In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations...` with `func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations...`.

4. In `rollup/cmd/rollup_relayer/app/app.go`, the patch replaces `l2watcher := watcher.NewL2WatcherClient(subCtx, l2client, cfg.L2Config.Confirmations,...` with `l2watcher := watcher.NewL2WatcherClient(subCtx, l2client, cfg.L2Config.Confirmations,...`.

## Project Context

The changed code sits primarily in `rollup/internal/controller/watcher`, `rollup/internal/controller`, `rollup/cmd/rollup_relayer/app`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rollup/internal/controller/watcher/l2_watcher_test.go`, `rollup/internal/controller/watcher/proposer_tool.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rollup/internal/controller/watcher/l2_watcher_test.go`, `rollup/internal/controller/sender/sender_test.go`. The strongest project-level identifiers around this patch are `L2Config`, `block`, `count`, and `NewL2WatcherClient`.

## Before/After Behavior

Before the patch, `GetAndStoreBlocks` counted L1 message transactions from the block and then continued into the existing downstream path without a validium-specific substitution of message inputs. After the patch, the watcher gains a `validiumMode` flag and, when that mode is enabled and the block contains L1 messages, it fetches the original encrypted L1 messages for that block and errors out if retrieval fails. Startup wiring now passes the configured validium flag into the watcher.

# Root Cause

The watcher previously lacked an explicit validium-mode input-selection path for original encrypted L1 messages, so downstream processing in validium mode could proceed using the ordinary block transaction representation instead of the intended original message source.

## Walkthrough

1. `GetAndStoreBlocks` retrieves a block and counts L1 message transactions from `blockTxs`.

2. A new branch is added immediately afterward with the comment `use original (encrypted) L1 message txs in validium mode`.

3. Inside that branch, if the block has L1 message transactions, the watcher calls `GetL1MessagesInBlock(..., block.Hash(), eth.QueryModeSynced)` and returns an error if the fetch fails.

4. `L2WatcherClient` is extended to store `validiumMode`, and its constructor now accepts that flag.

5. The relayer app now passes `cfg.L2Config.RelayerConfig.ValidiumMode` into `NewL2WatcherClient`, so the new behavior is enabled from configuration.

6. The commit subject mentions `use original l1 msg hash for msg queue hash`, but the provided diff does not show the actual msg-queue hash computation, so only the upstream input-source change is directly evidenced.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rollup/internal/controller/watcher/l2_watcher.go | 95 | L2 watcher block-ingestion path that counts L1 message txs and, in validium mode, switches to fetching original encrypted L1 messages for downstream processing |
| rollup/internal/controller/watcher/l2_watcher.go | 43 | Watcher constructor/state that introduces `validiumMode` as a behavioral switch for canonical message-source selection |
| rollup/cmd/rollup_relayer/app/app.go | 112 | Relayer wiring that propagates configured validium mode into the watcher so the correct hashing path is actually used in production |

## Code Snippets

## Snippet 1

Context: `rollup/internal/controller/watcher/l2_watcher.go:112` (changes signature or replay validation logic)

Before
```go
log.Info("retrieved block", "height", block.Header().Number, "hash", block.Header().Hash().String(), "L1 message count", count)

		withdrawRoot, err3 := w.StorageAt(ctx, w.messageQueueAddress, w.withdrawTrieRootSlot, big.NewInt(int64(number)))
		if err3 != nil {
```
After
```go
log.Info("retrieved block", "height", block.Header().Number, "hash", block.Header().Hash().String(), "L1 message count", count)

		// use original (encrypted) L1 message txs in validium mode
		if w.validiumMode {
			var txs []*types.Transaction

			if count > 0 {
				log.Info("Fetching encrypted messages in validium mode")
```

## Snippet 2

Context: `rollup/internal/controller/watcher/l2_watcher.go:102` (changes a sensitive control or state-update path)

Before
```go
}

		var count int
		for _, tx := range block.Transactions() {
			if tx.IsL1MessageTx() {
				count++
```
After
```go
}

		blockTxs := block.Transactions()

		var count int
		for _, tx := range blockTxs {
			if tx.IsL1MessageTx() {
				count++
```

## Snippet 3

Context: `rollup/internal/controller/watcher/l2_watcher.go:43` (changes signature or replay validation logic)

Before
```go
// NewL2WatcherClient take a l2geth instance to generate a l2watcherclient instance
func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations rpc.BlockNumber, messageQueueAddress common.Address, withdrawTrieRootSlot common.Hash, chainCfg *params.ChainConfig, db *gorm.DB, reg prometheus.Registerer) *L2WatcherClient {
	return &L2WatcherClient{
		ctx:    ctx,
```
After
```go
// NewL2WatcherClient take a l2geth instance to generate a l2watcherclient instance
func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations rpc.BlockNumber, messageQueueAddress common.Address, withdrawTrieRootSlot common.Hash, chainCfg *params.ChainConfig, db *gorm.DB, validiumMode bool, reg prometheus.Registerer) *L2WatcherClient {
	return &L2WatcherClient{
		ctx:    ctx,
```

## Snippet 4

Context: `rollup/cmd/rollup_relayer/app/app.go:112` (changes persisted or aggregate state handling)

Before
```go
bundleProposer := watcher.NewBundleProposer(subCtx, cfg.L2Config.BundleProposerConfig, minCodecVersion, genesis.Config, db, registry)

	l2watcher := watcher.NewL2WatcherClient(subCtx, l2client, cfg.L2Config.Confirmations, cfg.L2Config.L2MessageQueueAddress, cfg.L2Config.WithdrawTrieRootSlot, genesis.Config, db, registry)

	if cfg.RecoveryConfig != nil && cfg.RecoveryConfig.Enable {
```
After
```go
bundleProposer := watcher.NewBundleProposer(subCtx, cfg.L2Config.BundleProposerConfig, minCodecVersion, genesis.Config, db, registry)

	l2watcher := watcher.NewL2WatcherClient(subCtx, l2client, cfg.L2Config.Confirmations, cfg.L2Config.L2MessageQueueAddress, cfg.L2Config.WithdrawTrieRootSlot, genesis.Config, db, cfg.L2Config.RelayerConfig.ValidiumMode, registry)

	if cfg.RecoveryConfig != nil && cfg.RecoveryConfig.Enable {
```

# Fix Pattern

Introduce mode-aware canonical input selection before downstream processing, and fail closed if the mode-specific source data cannot be retrieved.

## How It Was Fixed

The patch threads a `validiumMode` boolean into the watcher, enables it from relayer configuration, and adds a validium-only fetch path that retrieves original encrypted L1 messages for the current block before later processing continues. This is a targeted input-source correction rather than a broadly evidenced vulnerability remediation.

# Why It Matters

1. It changes the data source feeding a queue-hash-related path, so correctness of later derived values depends on it.

2. The patch is explicitly limited to validium mode, which narrows the supported claim.

3. Failing when the original messages cannot be fetched avoids silently continuing with possibly wrong inputs.

4. The evidence does not show attacker control, authorization bypass, fund loss, or consensus failure.

# Evidence Notes

Strongest support comes from three facts in the provided material: the commit subject references using the original L1 message hash for the msg queue hash; `l2_watcher.go` adds a validium-only branch explicitly labeled for original encrypted L1 messages; and `app.go` wires `ValidiumMode` into the watcher constructor. What is not shown is the downstream hash computation itself, any proof that the previous behavior was externally exploitable, or any concrete impact beyond incorrect input selection for later processing. Protocol security invariant: The patch suggests a mode-specific integrity invariant: when validium mode is enabled, downstream queue-hash-related processing should use the original encrypted L1 message transactions for the block, not whatever representation is present in the normal block transaction list. The provided evidence does not show the full hash computation, so this invariant is inferred from the commit subject and the added branch comment. Verification notes: The patch does not show the full downstream msg-queue hash computation, only the changed input-selection path. The patch does not prove an external attacker could arbitrarily forge messages or bypass authorization. The patch does not establish whether the prior bug caused consensus failure, bridge safety impact, or only relayer/prover incompatibility. The evidence is specific to validium mode; it does not show the same issue in non-validium operation. The patch does not quantify exploit preconditions, affected versions, or real-world impact. The provided diff does not include the code that actually computes or stores the msg queue hash. No test changes or failure reproducer are included in the evidence. The security relevance is plausible but not established from the supplied material alone. The supported conclusion is a validium-specific integrity/correctness fix in message sourcing, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `canonical-input-selection`
Final impact type: `hash-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, validium, message-queue, hashing, fail-closed`

The patch is in a security-sensitive blockchain message-processing path and explicitly changes which L1 message data is used for a msg-queue-hash-related flow in validium mode. It also switches the watcher to fetch the original encrypted L1 messages and aborts if that retrieval fails, which is a clear integrity-tightening and fail-closed change. The evidence still does not prove a concrete exploitable vulnerability, attacker-controlled abuse path, or specific protocol break, so the strongest supported classification is security hardening rather than a confirmed security fix.

## Security Evidence

1. Commit subject ties the change to using the original L1 message hash for the msg queue hash.
2. The watcher adds a validium-only branch explicitly for original encrypted L1 message transactions.
3. The new path fetches L1 messages by block hash instead of relying only on the normal block transaction representation.
4. The code now returns an error if the original messages cannot be fetched, preventing silent continuation with possibly wrong inputs.
5. Application wiring passes configured ValidiumMode into the watcher, making the stricter behavior effective in production.

## Missing Evidence

1. The provided diff does not show the downstream msg queue hash computation itself.
2. No test, reproducer, or failing case is included to show the prior behavior caused a security failure.
3. No evidence shows attacker control, authorization bypass, fund loss, or consensus failure.
4. The patch alone does not quantify affected versions, exploitability, or real-world impact.

## Claim Boundaries

1. The supported claim is limited to validium-mode message-source and hash-input integrity hardening.
2. It is not proven from this patch alone that the prior behavior was an exploitable vulnerability.
3. The evidence supports fail-closed handling and canonical input selection, not a demonstrated state-corruption incident.
4. Any broader claims about bridge compromise, consensus impact, or asset loss go beyond the supplied evidence.
