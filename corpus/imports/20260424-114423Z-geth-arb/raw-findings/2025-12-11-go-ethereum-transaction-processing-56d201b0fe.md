---
case_id: case_20251211_56d201b0fe
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2025-12-11
source_refs:
  - git:56d201b0feb90b3e4a863349d0883c5502bc792f
  - "eth/handler.go:180"
  - "core/txpool/txpool.go:490"
  - "eth/fetcher/tx_fetcher.go:236"
  - "eth/fetcher/tx_fetcher_test.go:1909"
bug_class: peer-triggered-bandwidth-waste
impact_type:
  - limited-bandwidth-waste
  - resource-consumption
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - p2p
  - metadata-validation
  - bandwidth-waste
  - resource-consumption
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds announcement-time metadata validation to go-ethereum's transaction fetcher. Before scheduling fetch work, the fetcher now checks both whether the hash is already known and whether the announced transaction type is supported by the local txpool. The supported security claim is limited peer-triggered bandwidth waste reduction, not consensus validation, txpool state corruption, cryptographic correctness, or an unbounded denial of service.

## Observed Patch Facts

1. In `eth/handler.go`, the patch replaces `h.txFetcher = fetcher.NewTxFetcher(h.txpool.Has, addTxs, fetchTx, h.removePeer)` with `validateMeta := func(tx common.Hash, kind byte) error {`.

2. In `core/txpool/txpool.go`, the patch adds `// FilterType returns whether a transaction with the given type is supported`.

3. In `eth/fetcher/tx_fetcher.go`, the patch replaces `switch {` with `err := f.validateMeta(hash, types[i])`.

4. In `eth/fetcher/tx_fetcher_test.go`, the patch replaces `func testTransactionFetcherParallel(t *testing.T, tt txFetcherTest) {` with `func TestTransactionFetcherWrongMetadata(t *testing.T) {`.

## Project Context

The changed code sits primarily in `core/txpool`, `eth/fetcher`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/handler_test.go`, `core/txpool/subpool.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/subpool.go`, `core/txpool/legacypool/legacypool.go`. The strongest project-level identifiers around this patch are `txpool`, `kind`, `types`, and `hash`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/supply_test.go`, `eth/tracers/internal/tracetest/prestate_test.go`.

## Before/After Behavior

Before the patch, the handler constructed the transaction fetcher with only `h.txpool.Has`, and `TxFetcher.Notify` filtered already-known or underpriced hashes before treating remaining announcements as candidates for tracking and fetch scheduling. The supplied evidence does not show an announcement-time check for whether the advertised transaction type was supported. After the patch, the handler passes a `validateMeta(hash, kind)` callback that rejects already-known hashes and unsupported transaction types using `h.txpool.FilterType(kind)`. `TxPool.FilterType` returns true when any configured subpool supports the type, and `Notify` skips announcements when metadata validation returns an error.

# Root Cause

The announcement path accepted unknown transaction hashes for fetch scheduling without first checking whether the peer-advertised transaction type was supported by the local txpool. This could let peers cause fetch work for announcements carrying arbitrary or unsupported type metadata, although later fetched-body validation still applied.

## Walkthrough

1. A peer announces transaction hashes with metadata including transaction type bytes.

2. Before the patch, the fetcher checked whether a hash was already known or known-underpriced, then could schedule unknown hashes for fetching.

3. The provided before-code evidence does not show a supported-transaction-type check before fetch scheduling.

4. The patch introduces a `validateMeta` callback at handler construction time.

5. The callback preserves duplicate-hash rejection and adds a txpool type-support check through `FilterType`.

6. `Notify` now calls `validateMeta(hash, types[i])` before tracking or fetching an announcement.

7. Announcements with unsupported metadata are skipped rather than scheduled for fetch work.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/handler.go | 180 | constructs tx fetcher metadata validator using txpool.Has and txpool.FilterType |
| core/txpool/txpool.go | 490 | adds aggregate transaction type support check across subpools |
| eth/fetcher/tx_fetcher.go | 236 | filters transaction announcements by metadata before tracking or fetching |
| eth/fetcher/tx_fetcher_test.go | 1909 | regression coverage for announcements with wrong or unsupported metadata |

## Code Snippets

## Snippet 1

Context: `eth/handler.go:180` (changes signature or replay validation logic)

Before
```go
return h.txpool.Add(txs, false)
	}
	h.txFetcher = fetcher.NewTxFetcher(h.txpool.Has, addTxs, fetchTx, h.removePeer)
	return h, nil
}
```
After
```go
return h.txpool.Add(txs, false)
	}

	validateMeta := func(tx common.Hash, kind byte) error {
		if h.txpool.Has(tx) {
			return txpool.ErrAlreadyKnown
		}
		if !h.txpool.FilterType(kind) {
```

## Snippet 2

Context: `core/txpool/txpool.go:490` (changes a sensitive control or state-update path)

Before
```go
}
}
```
After
```go
}
}

// FilterType returns whether a transaction with the given type is supported
// (can be added) by the pool.
func (p *TxPool) FilterType(kind byte) bool {
	for _, subpool := range p.subpools {
		if subpool.FilterType(kind) {
```

## Snippet 3

Context: `eth/fetcher/tx_fetcher.go:236` (changes signature or replay validation logic)

Before
```go
)
	for i, hash := range hashes {
		switch {
		case f.hasTx(hash):
			duplicate++
		case f.isKnownUnderpriced(hash):
			underpriced++
		default:
```
After
```go
)
	for i, hash := range hashes {
		err := f.validateMeta(hash, types[i])
		if errors.Is(err, txpool.ErrAlreadyKnown) {
			duplicate++
			continue
		}
		if err != nil {
```

## Snippet 4

Context: `eth/fetcher/tx_fetcher_test.go:1909` (changes signature or replay validation logic)

Before
```go
}

func testTransactionFetcherParallel(t *testing.T, tt txFetcherTest) {
	t.Parallel()
```
After
```go
}

func TestTransactionFetcherWrongMetadata(t *testing.T) {
	testTransactionFetcherParallel(t, txFetcherTest{
		init: func() *TxFetcher {
			return NewTxFetcher(
				func(_ common.Hash, kind byte) error {
					switch kind {
```

# Fix Pattern

Add a cheap validation gate at the peer-announcement boundary before allocating fetcher tracking state or issuing network fetch requests.

## How It Was Fixed

`eth/handler.go` builds a metadata validator from `h.txpool.Has` and `h.txpool.FilterType`. `core/txpool/txpool.go` adds an aggregate `TxPool.FilterType(kind byte)` over subpools. `eth/fetcher/tx_fetcher.go` invokes the validator in `Notify` and skips announcements that fail validation. `eth/fetcher/tx_fetcher_test.go` adds regression coverage for wrong or unsupported metadata.

# Why It Matters

1. Reduces peer-triggered transaction-fetch bandwidth waste.

2. Rejects unsupported announced transaction types earlier.

3. Does not establish consensus-invalid transaction acceptance.

4. Does not establish txpool state corruption or unbounded DoS.

# Evidence Notes

The strongest evidence is the new `validateMeta` callback in `eth/handler.go`, the new `TxPool.FilterType` method in `core/txpool/txpool.go`, the `Notify` validation call in `eth/fetcher/tx_fetcher.go`, and the wrong-metadata regression test. The commit message explicitly bounds impact to wasting a limited portion of victim bandwidth and says fetched-body validation and protocol-violation handling still occur later. Claims about state corruption, replay, cryptography, or catastrophic denial of service are unsupported. Protocol security invariant: Transaction announcements from peers should not trigger fetch scheduling when the advertised transaction type is unsupported by the local txpool; final fetched-body validation remains the authority for transaction validity. Verification notes: No consensus-invalid transaction acceptance is shown. No txpool state corruption is shown. No bypass of fetched body validation is shown. No catastrophic or unbounded denial of service is proven. No cryptographic or replay invariant change is evidenced beyond transaction type metadata filtering. Commit text describes a bug with limited bandwidth-waste impact. Implementation rejects unsupported transaction types at announcement time. Regression test covers wrong metadata behavior. No supplied evidence shows final transaction validation was bypassed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `peer-triggered-bandwidth-waste`
Final impact type: `limited-bandwidth-waste, resource-consumption`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, p2p, metadata-validation, bandwidth-waste, resource-consumption`

The supplied evidence supports a conservative security-hardening classification: the patch adds announcement-time validation so peers cannot cause transaction fetch work for unsupported transaction types. The commit message explicitly frames the impact as an attacker wasting a limited portion of victim bandwidth, while also stating later fetched-body validation still prevents type mismatch acceptance. The original state-corruption, state-integrity, consensus, snapshot, and database framing is not supported.

## Security Evidence

1. Commit message says an attacker could waste a limited portion of victim bandwidth.
2. Handler now constructs a validateMeta callback that rejects already-known hashes and unsupported transaction types.
3. TxPool gains FilterType to decide whether a transaction type can be accepted by any subpool.
4. TxFetcher Notify now validates hash/type metadata before tracking or fetching announced transactions.
5. Regression coverage is described for wrong or unsupported transaction metadata.

## Missing Evidence

1. No evidence of consensus-invalid transaction acceptance.
2. No evidence of txpool state corruption.
3. No evidence of cryptographic, replay, snapshot, or database integrity impact.
4. No evidence of unbounded denial of service or catastrophic resource exhaustion.
5. No evidence that final fetched-body validation was bypassed.

## Claim Boundaries

1. Validated only as early rejection of unsupported peer-announced transaction metadata.
2. Impact should be limited to peer-triggered bandwidth or fetch-work reduction.
3. Do not claim state corruption, consensus failure, or state-integrity compromise.
4. Do not classify as a concrete security-fix beyond hardening without stronger exploit evidence.
