---
case_id: case_20170622_0042f13d4
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
bug_class: resource-exhaustion
impact_type:
  - remote-dos
confidence: medium
source_quality: high
tags:
  - infrastructure
  - storage
  - resource-exhaustion
  - remote-dos
  - queue
  - database
date: 2017-06-22
source_refs:
  - git:0042f13d47700987e93e413be549b312e81854ac
  - "eth/downloader/downloader.go:932"
  - "trie/sync.go:216"
  - "eth/downloader/queue.go:859"
  - "eth/downloader/downloader.go:1294"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security hardening for go-ethereum fast/state sync denial-of-service risk. The strongest supported claim is not state corruption, cryptographic failure, or consensus invalidity, but resource-control hardening around state trie node downloads, stale peer responses, duplicate retrievals, request leaks, and sync hangs.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `// fetchNodeData iteratively downloads the scheduled state trie nodes, taking any` with `// fetchParts iteratively downloads scheduled block parts, taking any available`.

2. In `trie/sync.go`, the patch replaces `// Pending returns the number of state entries currently pending for download.` with `// Commit flushes the data stored in the internal membatch out to persistent`.

3. In `eth/downloader/queue.go`, the patch replaces `// DeliverNodeData injects a node state data retrieval response into the queue.` with `// Prepare configures the result cache to allow accepting and caching inbound`.

4. In `eth/downloader/downloader.go`, the patch replaces `// processContent takes fetch results from the queue and tries to import them` with `// processFullSyncContent takes fetch results from the queue and imports them into th...`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `storage` area of the project. Historical context from `trie/sync_test.go`, `trie/errors.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/downloader_test.go`, `eth/downloader/statesync.go`. The strongest project-level identifiers around this patch are `error`, `queue`, `results`, and `data`.

## Before/After Behavior

Before the patch, state trie node downloads were handled through the shared downloader queue via `fetchNodeData` and `DeliverNodeData`, where scheduling could hold the queue lock and the commit body states this caused timeouts for other requests. The commit body also describes stale deliveries, duplicate retrievals, overwritten pending requests after peer reconnect, and failure accounting reset on mere delivery rather than persisted progress. After the patch, state sync is separated from the shared queue, trie sync rejects unrequested or already processed results, progress is tied to committed data, and content processing/pivot handling is split to coordinate state sync separately.

# Root Cause

State-sync request and progress accounting could diverge from actual useful persisted trie progress. Stale or duplicate peer deliveries and quick peer reconnects could affect idle/retry/failure state incorrectly, causing overlapping requests, leaked requests that were not retried, duplicate retrieval storms, or repeated attacker-driven sync failure loops.

## Walkthrough

1. A node performing fast/state sync requests trie node data from peers.

2. In the old path, state-node delivery was coupled to the shared downloader queue and `DeliverNodeData` looked up pending state requests under the queue lock.

3. The commit body states state-node scheduling could hog that lock and cause timeouts for other downloader requests.

4. The commit body further states stale deliveries could mark peers idle and lead to multiple in-flight requests and mass duplicate retrievals.

5. A peer drop followed by quick reconnect could overwrite a pending state task, leaking the old request so it was never retried.

6. Trie sync now rejects unrequested and already processed results instead of treating them as normal useful deliveries.

7. Progress/failure accounting is tied to actual committed trie data through processing and commit reporting, not merely receiving peer data.

8. State sync is moved out of the shared queue path, reducing cross-request lock contention and isolating state-sync timeout/retry behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/statesync.go | 28 | Tracks state sync requests, peer assignment, response data, timeouts, and retry behavior for state trie node downloads. |
| eth/downloader/downloader.go | 913 | Separates generic block part fetching from state-node sync so state downloads no longer hog the shared downloader queue lock. |
| eth/downloader/downloader.go | 1294 | Processes downloaded content and pivot-block handling while coordinating independent state sync completion/failure. |
| trie/sync.go | 174 | Processes delivered trie sync results, rejects unrequested/already processed data, schedules children, and records whether processing actually committed data. |
| trie/sync.go | 216 | Flushes trie sync membatch to persistent storage so downloader progress accounting can be based on written state. |
| eth/downloader/queue.go | 859 | Former queue-based state-node delivery path where stale delivery and pending-request accounting were coupled to the shared downloader queue. |

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

Separate high-latency untrusted state-node sync from shared downloader scheduling, reject stale or duplicate peer responses, retry leaked or timed-out work explicitly, and count progress only after trie data is committed.

## How It Was Fixed

The patch removes the queue-based state-node fetch/delivery path from the generic downloader queue and uses independent state-sync tracking. It keeps generic block-part fetching in `fetchParts`, splits content processing paths, validates trie sync results against outstanding requests, reports whether processing actually committed data, and flushes the trie sync membatch through `Commit`. The commit body also states pending assignments are moved back to retry handling and stale deliveries no longer cause overlapping work.

# Why It Matters

1. Limits sync-level denial of service from malicious or faulty peers.

2. Prevents stale or duplicate state deliveries from being counted as useful progress.

3. Reduces duplicate retrieval storms and queue lock contention.

4. Avoids leaked state requests that can hang sync.

5. Keeps failure accounting aligned with persisted trie progress.

# Evidence Notes

The commit is mostly a downloader/state-sync refactor and correctness cleanup, but the provided body identifies concrete adversarial resource-control behavior: resetting pivot fail count on mere delivery lets an attacker loop indefinitely unless data is written to disk, stale deliveries can cause overlapping in-flight requests and mass duplicate retrievals, and peer reconnects can leak state requests so they are never retried. The affected path is Ethereum fast sync state trie retrieval rather than general storage corruption. The evidence supports a likely DoS/resource-exhaustion hardening classification, not a proven consensus or state-integrity exploit. Protocol security invariant: During fast/state sync, untrusted peer state-node responses must match outstanding requests and must not reset retry or failure accounting unless they produce committed trie data; stale, duplicate, or unexpected deliveries must not create overlapping requests or leaked work. Verification notes: The patch does not prove remote code execution or cryptographic breakage. The patch does not prove consensus state corruption or acceptance of invalid trie data. The patch does not prove theft, replay, or transaction authorization bypass. The strongest supported security claim is sync-level denial-of-service or resource exhaustion by malicious or misbehaving peers. Large parts of the commit are refactor, cleanup, and test stabilization rather than independently security-relevant changes. No independent advisory or CVE evidence is provided. No exploit proof is provided beyond the commit body's attacker-loop description. The strongest grounded classification is resource-exhaustion hardening in fast/state sync. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The evidence supports retaining this as security hardening for resource-exhaustion/DoS risk in fast/state sync. Much of the commit is refactor, correctness, and reliability work, but the commit body explicitly describes attacker-controllable looping via failure accounting not tied to disk progress, stale deliveries causing duplicate retrieval storms, and request leaks/hangs in peer-driven state sync. The supplied code evidence shows changes in untrusted trie sync result handling, queue removal, request/progress accounting, and commit-based progress, which is enough for security-hardening but not a proven concrete security-fix.

## Security Evidence

1. Commit body explicitly states that if progress is reset on delivery rather than disk writes, an attacker can loop and attack indefinitely.
2. Commit body describes stale deliveries causing overlapping in-flight requests and mass duplicate retrievals between peers.
3. Commit body describes peer reconnect behavior leaking requests so they are never retried, causing state sync hangs.
4. Patch evidence shows trie sync rejecting unrequested and already processed results through ErrNotRequested and ErrAlreadyProcessed paths.
5. Patch evidence shows state sync separated from the shared downloader queue, reducing lock contention and timeout amplification.

## Missing Evidence

1. No advisory, CVE, issue, or external exploit report is provided.
2. No direct test or proof demonstrates a malicious remote peer reliably causing node-wide denial of service.
3. The patch also contains broad refactoring, cleanup, batching, and reliability changes that are not independently security-specific.
4. The evidence does not prove consensus failure, invalid state acceptance, theft, replay, or cryptographic compromise.

## Claim Boundaries

1. Classify as resource-exhaustion or sync-level remote DoS hardening, not as state corruption or consensus bypass.
2. Do not claim remote code execution, authorization bypass, or cryptographic weakness.
3. Do not treat every touched downloader or trie change in the commit as security-relevant.
4. The strongest supported claim is that peer-supplied stale, duplicate, or unexpected state sync data could worsen retries, hangs, or duplicate work unless tightly accounted.
