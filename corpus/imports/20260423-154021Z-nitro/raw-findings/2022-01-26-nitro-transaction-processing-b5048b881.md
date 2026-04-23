---
case_id: case_20220126_b5048b881
project: nitro
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
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
bug_class: missing-payment-validation
impact_type:
  - unauthorized-service-use
  - fee-bypass
confidence: medium
tags:
  - blockchain-core
  - sequencer
  - admission-control
  - payment-routing
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied diff supports a likely security-relevant admission-control fix in the sequencer: before, the shown publish path serialized submitted transactions without an evident check that the sender's pricing configuration pointed at this sequencer; after, `preTxFilter` rejects senders whose `PreferredAggregator` is not `SequencerAddress`. The streamer and block-processor changes look like support code for carrying rejection/parse outcomes, not the primary root cause.

## Observed Patch Facts

1. In `arbos/block_processor.go`, the patch replaces `state, err := arbosState.OpenSystemArbosState(statedb, true)` with `txes, err := message.ParseL2Transactions(chainConfig.ChainID)`.

2. In `arbnode/transaction_streamer.go`, the patch replaces `func (s *TransactionStreamer) SequenceMessages(messages []*arbos.L1IncomingMessage) e...` with `func messageFromTxes(header *arbos.L1IncomingMessageHeader, txes types.Transactions,...`.

3. In `arbnode/sequencer.go`, the patch replaces `func (s *Sequencer) Start(ctx context.Context) error {` with `func preTxFilter(state *arbosState.ArbosState, tx *types.Transaction, sender common.A...`.

4. In `arbnode/sequencer.go`, the patch replaces `txBytes, err := tx.MarshalBinary()` with `resultChan := make(chan error, 1)`.

## Project Context

Historical context from `arbos/incomingmessage.go`, `arbnode/inbox_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbnode/inbox_test.go`, `arbnode/delayed.go`. The strongest project-level identifiers around this patch are `error`, `txes`, `types`, and `l2Message`.

## Before/After Behavior

Before the change, the visible `PublishTransaction` path in `arbnode/sequencer.go` immediately marshaled a transaction into an L2 message, and the provided excerpts do not show a prior `PreferredAggregator` check in that ingress path. After the change, `preTxFilter(state, tx, sender)` reads `state.L1PricingState().PreferredAggregator(sender)` and returns an error unless it equals `l1pricing.SequencerAddress`. The publication flow also changes to queue the transaction with a `resultChan`, which supports returning accept/reject results. Separately, `arbnode/transaction_streamer.go` adds `messageFromTxes(..., txErrors)` and only uses the single signed-transaction encoding when there is no associated error, while `arbos/block_processor.go` parses L2 transactions from incoming messages and falls back safely on parse failure.

# Root Cause

A missing sequencer-side admission check allowed the shown transaction-ingress path to proceed without first verifying that the sender's ArbOS pricing configuration selected this sequencer as preferred aggregator. The later streamer and block-processing adjustments appear to propagate and tolerate resulting error states rather than assuming every submitted transaction is valid.

## Walkthrough

1. `arbnode/sequencer.go` adds `preTxFilter(state, tx, sender)`.

2. That filter calls `state.L1PricingState().PreferredAggregator(sender)` and returns an error when the result is not `l1pricing.SequencerAddress`.

3. The same file changes `PublishTransaction` away from immediate inline serialization toward a queued path with `resultChan`, supporting explicit rejection reporting.

4. `arbnode/transaction_streamer.go` adds `messageFromTxes(header, txes, txErrors)`, checks `len(txErrors) == len(txes)`, and only emits the simple single-transaction `SignedTx` path when `txErrors[0] == nil`.

5. `arbos/block_processor.go` now parses transactions from the incoming message with `message.ParseL2Transactions(chainConfig.ChainID)`, logs parse errors, and uses an empty transaction list on failure.

6. Taken together, the core fix is the new sequencer admission check; the other changes support handling rejected or non-parseable inputs safely.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbnode/sequencer.go | 61 | sequencer admission filter enforcing sender preferred-aggregator == sequencer |
| arbnode/sequencer.go | 42 | transaction publication path updated to return filter/rejection results instead of blindly serializing |
| arbnode/transaction_streamer.go | 262 | message construction path carrying per-transaction error handling for sequenced input |
| arbos/block_processor.go | 83 | block-production path parsing L2 transactions from incoming messages after sequencing/filtering |

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

Add an explicit authorization/payment-routing check at the service ingress point, then propagate rejection state through downstream encoding and consumption paths instead of assuming all submitted inputs are valid.

## How It Was Fixed

The patch introduces a pre-sequencing filter that consults ArbOS L1 pricing state and rejects transactions whose sender does not prefer this sequencer as aggregator. It also restructures the publish path to return results asynchronously, adds error-aware message construction in the transaction streamer, and makes block production parse incoming L2 transactions with explicit failure handling.

# Why It Matters

1. It prevents use of sequencer service when the sender's pricing configuration does not point to that sequencer.

2. It reduces the chance that rejected input is still encoded downstream as an ordinary signed sequencer transaction.

3. It strengthens an economic/admission invariant, but the excerpts do not establish broader impacts like theft, double spend, or consensus failure.

# Evidence Notes

Direct evidence for the main claim is limited but sufficient for a likely admission-control issue: `preTxFilter` is new, reads `PreferredAggregator(sender)`, and rejects unless it matches `SequencerAddress`. The old `PublishTransaction` excerpt shows immediate `MarshalBinary`-based message creation and no visible equivalent check. The streamer and block-processor changes support safer handling of error cases, but they do not by themselves prove the security property. Exact fee mechanics and exploit scope are still inferred from the names `PreferredAggregator`, `SequencerAddress`, and the commit subject rather than fully shown in the excerpts. Protocol security invariant: The sequencer should not accept a transaction for sequencing unless ArbOS pricing state says the sender's preferred aggregator is this sequencer (`l1pricing.SequencerAddress`). Transactions failing that check should be rejected rather than treated as normal sequencer input. Verification notes: The patch does not prove a consensus failure or validator bypass. The patch does not show direct asset theft or double-spend behavior. The evidence does not establish how much an attacker could gain beyond obtaining sequencing service without paying the sequencer. The exact fee mechanics are inferred from `PreferredAggregator` and `SequencerAddress` naming, not fully shown in the patch. The provided evidence supports an admission/payment-routing fix more strongly than a generic serialization bug. Confidence is reduced because the full call chain into `preTxFilter` is not shown in the excerpts. No supplied excerpt proves asset loss, consensus breakage, validator bypass, or exact fee impact. The transaction streamer and block processor changes should be treated as supporting changes unless fuller code shows they were independently vulnerable. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-payment-validation`
Final impact type: `unauthorized-service-use, fee-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, sequencer, admission-control, payment-routing`

The patch clearly adds a sequencer-side gate that rejects transactions when the sender's `PreferredAggregator` is not this sequencer, and the commit subject explicitly frames the goal as rejecting transactions that do not pay it. That is security-sensitive admission/payment enforcement, but the supplied excerpts do not prove a concrete exploitable vulnerability beyond preventing unauthorized use of the sequencer service. The original phase-3 classification is too specific and misframed around serialization/state representation; this is better kept as a security-hardening case focused on payment/admission control.

## Security Evidence

1. `preTxFilter` is newly added and rejects when `PreferredAggregator(sender) != SequencerAddress`.
2. The commit subject states the intent: `Have sequencer reject transactions that don't pay it`.
3. `PublishTransaction` is reworked to return an acceptance/rejection result through `resultChan`, consistent with active ingress rejection.
4. `messageFromTxes(..., txErrors)` and parse-error handling in block production support safe downstream handling of rejected/invalid transactions.

## Missing Evidence

1. No supplied excerpt shows the full call path proving `preTxFilter` is invoked for every relevant transaction ingress path.
2. No patch excerpt proves asset theft, consensus failure, validator bypass, or cross-client divergence.
3. The exact fee mechanics and attacker benefit are inferred from names like `PreferredAggregator` and the commit subject, not fully demonstrated in code.

## Claim Boundaries

1. The evidence supports a sequencer payment/admission-control tightening, not a proven serialization bug.
2. The patch shows prevention of unauthorized sequencing service use; it does not prove broader protocol compromise.
3. The streamer and block-processor changes are supporting hardening changes, not standalone proof of separate security flaws.
