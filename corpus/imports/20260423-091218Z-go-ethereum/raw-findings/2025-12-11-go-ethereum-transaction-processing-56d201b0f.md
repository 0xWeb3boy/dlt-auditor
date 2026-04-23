---
case_id: case_20251211_56d201b0f
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2025-12-11
source_refs:
  - git:56d201b0feb90b3e4a863349d0883c5502bc792f
  - "eth/handler.go:180"
  - "core/txpool/txpool.go:490"
  - "eth/fetcher/tx_fetcher.go:236"
  - "eth/fetcher/tx_fetcher_test.go:1909"
bug_class: p2p-metadata-validation
impact_type:
  - bandwidth-waste
  - resource-consumption
tags:
  - blockchain-core
  - transaction-processing
  - p2p
  - transaction-fetcher
  - metadata-validation
  - resource-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens go-ethereum's transaction announcement handling by validating peer-supplied transaction type metadata before scheduling transaction body fetches. The supported security claim is limited bandwidth/resource waste from arbitrary unsupported type announcements, not consensus impact, transaction acceptance bypass, state corruption, or cryptographic failure.

## Observed Patch Facts

1. In `eth/handler.go`, the patch replaces `h.txFetcher = fetcher.NewTxFetcher(h.txpool.Has, addTxs, fetchTx, h.removePeer)` with `validateMeta := func(tx common.Hash, kind byte) error {`.

2. In `core/txpool/txpool.go`, the patch adds `// FilterType returns whether a transaction with the given type is supported`.

3. In `eth/fetcher/tx_fetcher.go`, the patch replaces `switch {` with `err := f.validateMeta(hash, types[i])`.

4. In `eth/fetcher/tx_fetcher_test.go`, the patch replaces `func testTransactionFetcherParallel(t *testing.T, tt txFetcherTest) {` with `func TestTransactionFetcherWrongMetadata(t *testing.T) {`.

## Project Context

The changed code sits primarily in `core/txpool`, `eth/fetcher`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/handler_test.go`, `core/txpool/subpool.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/subpool.go`, `core/txpool/legacypool/legacypool.go`. The strongest project-level identifiers around this patch are `txpool`, `kind`, `types`, and `hash`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/supply_test.go`, `eth/tracers/internal/tracetest/prestate_test.go`.

## Before/After Behavior

Before the patch, the tx fetcher prefiltered known and underpriced hashes but the provided evidence does not show a local txpool-supported-type check before unknown announcements could be retained for fetching. After the patch, the handler supplies validateMeta, which rejects already-known hashes and unsupported transaction types via TxPool.FilterType; Notify invokes this validator before scheduling fetch work.

# Root Cause

The fetcher accepted peer-supplied announcement metadata far enough to schedule fetches without first checking whether the announced transaction type was supported by the local txpool. The commit text says later body validation still rejected mismatched or unsupported responses, so the root cause is early metadata validation missing in the P2P fetch path.

## Walkthrough

1. A peer announces transaction hashes with per-hash type metadata.

2. The old Notify path filtered already-known and underpriced transactions, but the supplied diff does not show a txpool-supported-type check before unknown hashes were considered for fetch scheduling.

3. An unsupported or arbitrary announced type could therefore cause unnecessary transaction body fetch work.

4. The handler now constructs validateMeta to check knownness and local txpool type support.

5. TxPool.FilterType aggregates type support across subpools.

6. Notify now calls validateMeta for each announced hash and type and skips metadata errors other than the duplicate case.

7. The added test covers wrong metadata by rejecting unrecognized transaction type bytes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/handler.go | 180 | constructs tx fetcher metadata validator that rejects already-known hashes and unsupported transaction types |
| eth/fetcher/tx_fetcher.go | 236 | applies metadata validation during transaction announcement handling before scheduling unknown hashes for fetch |
| core/txpool/txpool.go | 490 | adds aggregate transaction-type support check across txpool subpools |
| eth/fetcher/tx_fetcher_test.go | 1909 | adds regression coverage for wrong or unsupported announcement metadata |

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

Validate untrusted P2P announcement metadata at the scheduling boundary using the same local capability model that downstream txpool acceptance relies on.

## How It Was Fixed

NewTxFetcher is given a metadata validator instead of only a hash-knownness predicate. The validator calls h.txpool.Has and h.txpool.FilterType. TxPool.FilterType was added to query subpool support, and Notify now rejects unsupported metadata before tracking or requesting the transaction body.

# Why It Matters

1. Reduces peer-induced bandwidth waste from unsupported transaction type announcements.

2. Keeps fetch scheduling aligned with local txpool capabilities.

3. Does not imply a validation bypass because fetched bodies are still checked later.

4. Does not establish consensus, fund-loss, replay, or state-corruption impact.

# Evidence Notes

Evidence comes from eth/handler.go adding validateMeta, core/txpool/txpool.go adding FilterType, eth/fetcher/tx_fetcher.go invoking validateMeta in Notify, and tx_fetcher_test.go adding wrong-metadata coverage. The commit body explicitly bounds impact to limited victim bandwidth waste and says mismatched fetched responses are treated as protocol violations. Claims of state corruption, cryptographic weakness, replay sensitivity, unbounded denial of service, or body validation bypass are unsupported. Protocol security invariant: Remote peers should not be able to make a node schedule or request transaction bodies for announced transaction types that the local txpool does not support. This invariant is limited to early fetch scheduling; final fetched-body validation still applies. Verification notes: Does not prove accepted transaction bodies could bypass txpool validation. Does not prove consensus state, replay protection, or cryptographic verification was affected. Does not prove unbounded denial of service; the commit describes only limited victim bandwidth waste. Does not prove remote code execution, fund loss, or chain split impact. Does not show state corruption despite the heuristic baseline label. No external context or file inspection was used. The classification is security-hardening rather than a confirmed vulnerability because the demonstrated impact is limited resource waste. Keep in corpus only as a low-impact P2P resource-hardening fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `p2p-metadata-validation`
Final impact type: `bandwidth-waste, resource-consumption`
Final tags: `blockchain-core, transaction-processing, p2p, transaction-fetcher, metadata-validation, resource-hardening`

The patch clearly adds early validation of untrusted transaction announcement metadata before scheduling transaction body fetches, rejecting unsupported transaction types via txpool capability checks. The supported security relevance is limited P2P resource hardening against bandwidth waste; the evidence does not support the original state-corruption, consensus, snapshot, or database-oriented framing.

## Security Evidence

1. Commit body states an attacker could waste a limited portion of a victim's bandwidth.
2. eth/handler.go adds validateMeta to reject already-known hashes and unsupported transaction types.
3. core/txpool/txpool.go adds FilterType to determine whether the local pool supports a transaction type.
4. eth/fetcher/tx_fetcher.go invokes validateMeta during Notify before tracking or fetching announced transactions.
5. A regression test covers wrong metadata / unsupported transaction type announcements.

## Missing Evidence

1. No evidence that unsupported announcements could bypass final transaction validation.
2. No evidence of consensus divergence, state corruption, fund loss, replay failure, or cryptographic weakness.
3. No evidence of unbounded denial of service beyond the limited bandwidth waste described in the commit body.

## Claim Boundaries

1. Keep only as low-impact P2P resource-hardening, not as a state-integrity fix.
2. Do not claim transaction bodies were accepted incorrectly; later validation still applies according to the commit body.
3. Do not claim consensus, snapshot, database, or cryptographic impact from this patch.
4. The attacker model is limited to peer-supplied transaction announcement metadata causing unnecessary fetch work.
