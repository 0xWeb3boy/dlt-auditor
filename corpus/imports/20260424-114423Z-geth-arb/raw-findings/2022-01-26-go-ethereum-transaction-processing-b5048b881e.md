---
case_id: case_20220126_b5048b881e
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2022-01-26
source_refs:
  - git:b5048b881ef126fa349a52d4ce80e3633e2c5aa4
  - "arbos/block_processor.go:89"
  - "arbnode/transaction_streamer.go:268"
  - "arbnode/sequencer.go:72"
  - "arbnode/sequencer.go:50"
bug_class: sequencer-fee-policy-bypass
impact_type:
  - fee-bypass
  - economic-abuse
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - sequencer
  - admission-control
  - fee-policy
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a sequencer-side admission filter that rejects transactions when the sender's preferred aggregator is not `l1pricing.SequencerAddress`. The evidence supports an economic admission-policy hardening: the sequencer now refuses transactions that, according to L1 pricing state, are not configured to pay it. The provided evidence does not prove fund theft, consensus failure, or validator acceptance of invalid transactions.

## Observed Patch Facts

1. In `arbos/block_processor.go`, the patch replaces `state, err := arbosState.OpenSystemArbosState(statedb, true)` with `txes, err := message.ParseL2Transactions(chainConfig.ChainID)`.

2. In `arbnode/transaction_streamer.go`, the patch replaces `func (s *TransactionStreamer) SequenceMessages(messages []*arbos.L1IncomingMessage) e...` with `func messageFromTxes(header *arbos.L1IncomingMessageHeader, txes types.Transactions,...`.

3. In `arbnode/sequencer.go`, the patch replaces `func (s *Sequencer) Start(ctx context.Context) error {` with `func preTxFilter(state *arbosState.ArbosState, tx *types.Transaction, sender common.A...`.

4. In `arbnode/sequencer.go`, the patch replaces `txBytes, err := tx.MarshalBinary()` with `resultChan := make(chan error, 1)`.

## Project Context

Historical context from `arbos/incomingmessage.go`, `arbnode/inbox_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbnode/inbox_test.go`, `arbnode/delayed.go`. The strongest project-level identifiers around this patch are `error`, `txes`, `types`, and `l2Message`.

## Before/After Behavior

Before the patch, the visible `PublishTransaction` path directly marshaled a submitted transaction into an L2 signed-transaction message, and the supplied evidence does not show a preferred-aggregator check before sequencing. After the patch, submitted transactions are queued with a result channel, `preTxFilter` checks `state.L1PricingState().PreferredAggregator(sender)`, and transactions are rejected if the preferred aggregator is not the sequencer. Supporting changes build incoming messages from transactions plus per-transaction errors and parse L2 transactions before block production.

# Root Cause

The sequencer admission path lacked an explicit check that the transaction sender's preferred L1 pricing aggregator was the sequencer. Based on the provided evidence, this allowed the sequencer publication path to proceed without enforcing that the sequencer was the configured L1 data-cost payment recipient.

## Walkthrough

1. A transaction is submitted through `Sequencer.PublishTransaction`.

2. The old visible path marshaled the transaction and constructed an L2 signed-transaction message directly.

3. The patch changes publication to enqueue the transaction with context and a result channel.

4. The new `preTxFilter` reads the sender's preferred aggregator from L1 pricing state.

5. If the preferred aggregator is not `l1pricing.SequencerAddress`, the transaction is rejected.

6. The transaction streamer constructs messages from accepted transactions and parallel per-transaction error results.

7. Block production parses L2 transactions from incoming messages before producing the block.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbnode/sequencer.go | 72 | adds sequencer pre-transaction filter requiring sender preferred aggregator to be the sequencer |
| arbnode/sequencer.go | 50 | changes transaction publication path to enqueue transactions and return asynchronous admission result |
| arbnode/transaction_streamer.go | 268 | builds sequenced L1 incoming messages from transactions plus per-transaction admission errors |
| arbos/block_processor.go | 89 | parses L2 transactions from incoming message before producing a block |

## Code Snippets

## Snippet 1

Context: `arbos/block_processor.go:89` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
chainConfig *params.ChainConfig,
) (*types.Block, types.Receipts) {

	state, err := arbosState.OpenSystemArbosState(statedb, true)
```
After
```go
chainConfig *params.ChainConfig,
) (*types.Block, types.Receipts) {
	txes, err := message.ParseL2Transactions(chainConfig.ChainID)
	if err != nil {
		log.Warn("error parsing incoming message", "err", err)
		txes = types.Transactions{}
	}
```

## Snippet 2

Context: `arbnode/transaction_streamer.go:268` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (s *TransactionStreamer) SequenceMessages(messages []*arbos.L1IncomingMessage) error {
	s.insertionMutex.Lock()
	defer s.insertionMutex.Unlock()

	pos, err := s.GetMessageCount()
```
After
```go
}

func messageFromTxes(header *arbos.L1IncomingMessageHeader, txes types.Transactions, txErrors []error) (*arbos.L1IncomingMessage, error) {
	if len(txErrors) != len(txes) {
		return nil, fmt.Errorf("unexpected number of error results: %v vs number of txes %v", len(txErrors), len(txes))
	}
	var l2Message []byte
	if len(txes) == 1 && txErrors[0] == nil {
```

## Snippet 3

Context: `arbnode/sequencer.go:72` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (s *Sequencer) Start(ctx context.Context) error {
	if s.l1Client == nil {
		return nil
	}

	initialBlockNr := atomic.LoadUint64(&s.l1BlockNumber)
```
After
```go
}

func preTxFilter(state *arbosState.ArbosState, tx *types.Transaction, sender common.Address) error {
	agg, _, err := state.L1PricingState().PreferredAggregator(sender)
	if err != nil {
		return err
	}
	if agg != l1pricing.SequencerAddress {
```

## Snippet 4

Context: `arbnode/sequencer.go:50` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func (s *Sequencer) PublishTransaction(ctx context.Context, tx *types.Transaction) error {
	txBytes, err := tx.MarshalBinary()
	if err != nil {
		return err
	}
	var l2Message []byte
	l2Message = append(l2Message, arbos.L2MessageKind_SignedTx)
```
After
```go
func (s *Sequencer) PublishTransaction(ctx context.Context, tx *types.Transaction) error {
	resultChan := make(chan error, 1)
	s.txQueue <- txQueueItem{
		tx,
		resultChan,
		ctx,
	}
```

# Fix Pattern

Add an admission-time economic policy check at the sequencer boundary and propagate per-transaction admission results into message construction.

## How It Was Fixed

The patch adds `preTxFilter` in `arbnode/sequencer.go`, which calls `PreferredAggregator(sender)` and requires the result to equal `l1pricing.SequencerAddress`. `PublishTransaction` is changed to route transactions through a queue that can return an admission result. `transaction_streamer.go` adds message construction from `txes` and `txErrors`, including a length consistency check. `block_processor.go` parses L2 transactions from incoming messages before using the more flexible block production path.

# Why It Matters

1. Prevents the sequencer from knowingly accepting transactions configured to pay a different aggregator.

2. Aligns transaction admission with L1 data-cost payment policy.

3. Provides explicit per-transaction admission errors instead of treating all submitted transactions as directly sequencable.

4. Does not establish consensus compromise or theft from the supplied evidence.

# Evidence Notes

The strongest evidence is the new `preTxFilter` in `arbnode/sequencer.go`, which rejects when `agg != l1pricing.SequencerAddress`. The commit subject supports the interpretation that the rejected transactions were considered not to pay the sequencer. The evidence is insufficient for stronger claims such as stolen funds, invalid block acceptance, replay failure, or consensus safety impact. Protocol security invariant: The sequencer should only admit transactions whose sender's L1 pricing preferred aggregator is the sequencer, so the transaction's L1 data-cost payment path is aligned with the sequencer publishing the transaction. Verification notes: Does not prove an attacker could steal funds or break consensus. Does not prove invalid transactions were accepted by validators after sequencing. Does not show the full tx queue processing loop or exact error encoding semantics. Does not establish impact beyond sequencer compensation/admission policy from the provided patch evidence. Verified only against the provided snippets and metadata. No full tx queue processing loop was provided. No test assertions or exact error serialization behavior were provided. Confidence is medium because the admission check is clear, but exploitability and security impact are not fully established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `sequencer-fee-policy-bypass`
Final impact type: `fee-bypass, economic-abuse`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, sequencer, admission-control, fee-policy`

The evidence supports a security-hardening classification, but not the original state-consistency/client-divergence framing. The patch adds an explicit sequencer admission check that rejects transactions whose sender's preferred aggregator is not the sequencer, matching the commit subject that the sequencer should reject transactions that do not pay it. This is best treated as economic/fee-policy hardening at the transaction admission boundary, not as a proven consensus, serialization, replay, or state-representation security fix.

## Security Evidence

1. New preTxFilter reads PreferredAggregator(sender) from L1 pricing state.
2. Transactions are rejected when the preferred aggregator is not l1pricing.SequencerAddress.
3. Commit subject says the sequencer should reject transactions that do not pay it.
4. PublishTransaction was changed from direct message construction to queued admission with a result channel, consistent with adding pre-sequencing checks.

## Missing Evidence

1. No proof of fund theft, consensus failure, replay issue, or validator acceptance of invalid transactions.
2. No full queue-processing loop or exact error propagation behavior is provided.
3. No test assertions are shown proving exploitability or externally observable abuse.
4. No evidence that the prior behavior allowed unbounded free execution rather than only a sequencer compensation policy mismatch.

## Claim Boundaries

1. Claim should be limited to sequencer-side admission and fee-payment policy hardening.
2. Do not classify as serialization, state-representation, or client-view divergence based on the supplied evidence.
3. Do not claim consensus safety impact, theft, or validator divergence.
4. The finding is retained as hardening, not as a confirmed concrete exploitable security fix.
