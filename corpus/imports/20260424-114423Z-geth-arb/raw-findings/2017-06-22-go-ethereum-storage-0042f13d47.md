---
case_id: case_20170622_0042f13d47
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2017-06-22
source_refs:
  - git:0042f13d47700987e93e413be549b312e81854ac
  - "eth/downloader/downloader.go:932"
  - "trie/sync.go:216"
  - "eth/downloader/queue.go:859"
  - "eth/downloader/downloader.go:1294"
bug_class: sync-availability-resource-amplification
impact_type:
  - availability
  - resource-exhaustion
tags:
  - infrastructure
  - downloader
  - state-sync
  - availability
  - resource-exhaustion
  - retry-accounting
  - peer-delivery
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports an availability hardening fix in go-ethereum's downloader state-sync path. The commit separates state sync from the shared downloader queue and repairs timeout, retry, stale-delivery, duplicate-delivery, and committed-progress accounting. The strongest security-relevant point is the commit text stating that resetting pivot failure accounting on merely delivered but unwritten state allowed an attacker to loop the sync without real progress.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `// fetchNodeData iteratively downloads the scheduled state trie nodes, taking any` with `// fetchParts iteratively downloads scheduled block parts, taking any available`.

2. In `trie/sync.go`, the patch replaces `// Pending returns the number of state entries currently pending for download.` with `// Commit flushes the data stored in the internal membatch out to persistent`.

3. In `eth/downloader/queue.go`, the patch replaces `// DeliverNodeData injects a node state data retrieval response into the queue.` with `// Prepare configures the result cache to allow accepting and caching inbound`.

4. In `eth/downloader/downloader.go`, the patch replaces `// processContent takes fetch results from the queue and tries to import them` with `// processFullSyncContent takes fetch results from the queue and imports them into th...`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `storage` area of the project. Historical context from `trie/sync_test.go`, `trie/errors.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/downloader_test.go`, `eth/downloader/statesync.go`. The strongest project-level identifiers around this patch are `error`, `queue`, `results`, and `data`.

## Before/After Behavior

Before the patch, state trie node downloads were coupled to the downloader queue, including delivery handling, timeout handling, peer idleness, and progress accounting. The commit text says this could cause queue-lock contention and timeouts, stale deliveries could incorrectly mark peers idle and lead to overlapping in-flight requests and duplicate retrievals, and a peer reconnect race could overwrite pending state requests so they were never retried. After the patch, state sync is handled independently of the generic queue path, timed-out or overwritten state requests are retried, stale or unexpected deliveries are not treated as useful progress, and trie sync distinguishes received data from committed storage progress.

# Root Cause

The root cause was overly loose state-sync request and progress accounting across queue scheduling, peer delivery handling, retry state, and trie persistence. Some paths could treat delivered data or task transitions as progress even when the data was stale, duplicate, unexpected, timed out, overwritten, or not written to disk.

## Walkthrough

1. The old `fetchNodeData` path scheduled state trie node downloads through the shared downloader queue.

2. The old `queue.DeliverNodeData` path handled pending state requests, stale deliveries, accepted counts, callbacks, and peer idleness in that queue-based flow.

3. The commit message says state-node scheduling could hog the queue lock and cause timeouts for other requests.

4. The commit message also says stale deliveries could mark peers idle, eventually producing overlapping in-flight requests and repeated stale deliveries across peers.

5. The commit text explicitly says pivot fail accounting was reset on delivered data rather than data written to disk, and that an attacker could loop this indefinitely.

6. The updated trie sync path rejects unrequested or already processed results and adds commit accounting for flushing membatch entries to persistent storage.

7. The state-sync changes retry timed-out requests and move overwritten pending assignments back to retry instead of leaking them.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 932 | removes queue-based node state fetching and separates state sync scheduling from generic block-part download scheduling |
| eth/downloader/queue.go | 859 | old state delivery path handled pending state requests, stale deliveries, peer idleness, and accepted/progress accounting under the downloader queue |
| trie/sync.go | 174 | processes returned trie state nodes, rejects unrequested or already processed data, and determines whether a delivery made committed progress |
| trie/sync.go | 216 | flushes trie sync membatch entries to persistent storage, making committed progress distinct from merely received data |
| eth/downloader/statesync.go | 28 | tracks per-peer state request tasks, timeout state, responses, and retry behavior for state sync |
| eth/downloader/downloader.go | 1294 | coordinates content import and state sync completion/failure around full and fast sync processing |

## Code Snippets

## Snippet 1

Context: `eth/downloader/downloader.go:932` (changes bounds, limits, or capacity handling)

Before
```go
}

// fetchNodeData iteratively downloads the scheduled state trie nodes, taking any
// available peers, reserving a chunk of nodes for each, waiting for delivery and
// also periodically checking for timeouts.
func (d *Downloader) fetchNodeData() error {
	log.Debug("Downloading node state data")
```
After
```go
}

// fetchParts iteratively downloads scheduled block parts, taking any available
// peers, reserving a chunk of fetch requests for each, waiting for delivery and
```

## Snippet 2

Context: `trie/sync.go:216` (changes a sensitive control or state-update path)

Before
```go
}

// Pending returns the number of state entries currently pending for download.
func (s *TrieSync) Pending() int {
```
After
```go
}

// Commit flushes the data stored in the internal membatch out to persistent
// storage, returning th enumber of items written and any occurred error.
func (s *TrieSync) Commit(dbw DatabaseWriter) (int, error) {
	// Dump the membatch into a database dbw
	for i, key := range s.membatch.order {
		if err := dbw.Put(key[:], s.membatch.batch[key]); err != nil {
```

## Snippet 3

Context: `eth/downloader/queue.go:859` (changes signature or replay validation logic)

Before
```go
}

// DeliverNodeData injects a node state data retrieval response into the queue.
// The method returns the number of node state accepted from the delivery.
func (q *queue) DeliverNodeData(id string, data [][]byte, callback func(int, bool, error)) (int, error) {
	q.lock.Lock()
	defer q.lock.Unlock()
```
After
```go
}

// Prepare configures the result cache to allow accepting and caching inbound
// fetch results.
```

## Snippet 4

Context: `eth/downloader/downloader.go:1294` (changes signature or replay validation logic)

Before
```go
}

// processContent takes fetch results from the queue and tries to import them
// into the chain. The type of import operation will depend on the result contents.
func (d *Downloader) processContent() error {
	pivot := d.queue.FastSyncPivot()
	for {
		results := d.queue.WaitResults()
```
After
```go
}

// processFullSyncContent takes fetch results from the queue and imports them into the chain.
func (d *Downloader) processFullSyncContent() error {
	for {
		results := d.queue.WaitResults()
		if len(results) == 0 {
			return nil
```

# Fix Pattern

Decouple state-sync scheduling from the shared downloader queue and make progress/retry decisions depend on outstanding request ownership and committed trie progress instead of mere receipt of peer data.

## How It Was Fixed

The patch removes the old queue-based state-node fetch and delivery path, coordinates state sync separately from block-part downloads, adds or relies on trie sync checks for unrequested and already processed results, introduces explicit commit accounting for trie sync writes, retries state requests on timeout, avoids treating stale deliveries as peer progress, and restores overwritten pending work to the retry path.

# Why It Matters

1. Protects node sync availability against peer-driven stale or duplicate delivery patterns.

2. Reduces resource amplification from repeated duplicate state retrievals.

3. Avoids sync hangs caused by leaked state requests after peer reconnect races.

4. Keeps failure accounting tied to persisted progress rather than mere receipt of data.

5. Does not establish a consensus validation bypass or invalid state acceptance issue.

# Evidence Notes

The security relevance is grounded mainly in the commit message, especially the attacker-loop statement around pivot fail accounting and the described duplicate retrieval and request-leak failure modes. The code excerpts support that the touched paths are downloader state sync, queue delivery, retry/timeout state, and trie commit accounting. Claims about theft, signature bypass, cryptographic failure, replay, or consensus-invalid state acceptance are not supported. Some parts of the commit are refactor, cleanup, batching, or test-stability work and should be treated as supporting changes rather than the vulnerability root cause. Protocol security invariant: During fast/state sync, peer-supplied state node responses should only advance sync accounting, reset failure counters, or free a peer for more work when they correspond to outstanding requests and produce real trie persistence progress; stale, duplicate, unexpected, timed-out, or overwritten requests must not create unbounded duplicate downloads or permanent sync hangs. Verification notes: The patch does not prove a consensus-validity bypass or acceptance of invalid Ethereum state. The evidence supports availability/resource-amplification risk, not theft, signature bypass, or cryptographic failure. The exact remote exploit preconditions are not fully shown beyond peer-controlled stale, duplicate, timeout, or reconnect behavior during sync. Large parts of the commit are refactor, cleanup, batching, and test-stability work; only the state sync accounting/retry paths carry the security relevance. The pivot receipt/block ordering change is not by itself shown to be a security flaw from the provided evidence. No external advisory or exploit proof is provided in the input. Remote preconditions are only partially established as peer delivery, timeout, stale response, or reconnect behavior during sync. The appropriate classification is availability hardening, not confirmed vulnerability fix. Helper and batching changes should not be treated as independent root causes without stronger evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `sync-availability-resource-amplification`
Final impact type: `availability, resource-exhaustion`
Final tags: `infrastructure, downloader, state-sync, availability, resource-exhaustion, retry-accounting, peer-delivery`

The evidence supports retaining this as security hardening, but not as a state-integrity or state-corruption fix. The commit text explicitly describes attacker-driven indefinite looping around pivot fail accounting, stale deliveries, duplicate retrievals, leaked requests, and timeout/retry behavior in peer-driven state sync. The patch evidence shows changes in downloader queue/state-sync handling and trie commit/progress accounting, which fits availability and resource-amplification hardening rather than a proven consensus or storage integrity vulnerability.

## Security Evidence

1. Commit text says resetting pivot fail count on delivered-but-unwritten nodes let an attacker loop the sync indefinitely.
2. Commit text describes stale deliveries causing overlapping in-flight requests and mass duplicate retrievals between peers.
3. Commit text describes leaked state requests after peer reconnects, causing state sync hangs.
4. Patch evidence touches downloader state-sync scheduling, timeout/retry behavior, queue delivery removal, and trie commit accounting.
5. TrieSync now distinguishes processed/requested data and committed persistent writes from mere receipt of peer data.

## Missing Evidence

1. No advisory, CVE, exploit proof, or externally documented vulnerability is provided.
2. Patch excerpts do not prove invalid state acceptance, consensus bypass, theft, replay, or cryptographic failure.
3. Remote attacker preconditions are only partially established from commit text, not demonstrated by tests or exploit code.
4. Large parts of the commit are refactor, cleanup, batching, and reliability work.

## Claim Boundaries

1. Classify as availability/resource-exhaustion hardening, not state corruption.
2. Do not claim state-integrity compromise or consensus validation failure.
3. Do not treat queue refactoring or batched writes alone as security fixes.
4. Security relevance is limited to peer-influenced state sync progress, retries, stale deliveries, duplicate retrievals, and hangs.
