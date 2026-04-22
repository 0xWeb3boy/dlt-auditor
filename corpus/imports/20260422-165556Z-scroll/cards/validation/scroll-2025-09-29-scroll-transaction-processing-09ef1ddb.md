# Validation Card

## Metadata

- ID: `scroll-2025-09-29-scroll-transaction-processing-09ef1ddb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-input-selection`

## What Confirmed The Issue

- Evidence 1: In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `withdrawRoot, err3 := w.StorageAt(ctx, w.messageQueueAddress, w.withdrawTrieRootSlot,...` with `// use original (encrypted) L1 message txs in validium mode`.
- Evidence 2: In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `for _, tx := range block.Transactions() {` with `blockTxs := block.Transactions()`.
- Evidence 3: In `rollup/internal/controller/watcher/l2_watcher.go`, the patch replaces `func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations...` with `func NewL2WatcherClient(ctx context.Context, client *ethclient.Client, confirmations...`.

## What Could Have Invalidated It

- Compensating control 1: If the alternate query path is guaranteed to return the exact same canonical transactions in the same order, a similar refactor may be less meaningful.
- Compensating control 2: The interesting signal is not variable renaming but the move to the authoritative transaction source for subsequent processing.
- Compensating control 3: The evidence supports watcher integrity hardening, not a demonstrated bridge exploit.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the alternate query path is guaranteed to return the exact same canonical transactions in the same order, a similar refactor may be less meaningful.
- Caution 2: The interesting signal is not variable renaming but the move to the authoritative transaction source for subsequent processing.
- Caution 3: The evidence supports watcher integrity hardening, not a demonstrated bridge exploit.
