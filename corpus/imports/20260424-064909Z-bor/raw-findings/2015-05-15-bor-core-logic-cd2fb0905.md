---
case_id: case_20150515_cd2fb0905
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
bug_class: resource-exhaustion
impact_type:
  - remote-dos
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - core-logic
  - resource-exhaustion
  - remote-dos
  - queue
date: 2015-05-15
source_refs:
  - git:cd2fb0905109828028172c84f9c10f1343647ca6
  - "eth/downloader/downloader.go:267"
  - "eth/downloader/queue.go:123"
  - "eth/sync.go:102"
  - "eth/downloader/downloader.go:28"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit progress check to the peer-driven hash download loop. Before the change, the downloader would continue querying a peer even when a non-final response added no new hashes to the queue. After the change, such a zero-progress response is treated as `ErrBadPeer`, and the synchronisation layer removes that peer. This supports a peer-triggered denial-of-service or resource-exhaustion fix in the downloader path.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `d.queue.Insert(hashPack.hashes)` with `// Insert all the new hashes, but only continue if got something useful`.

2. In `eth/downloader/queue.go`, the patch replaces `// Insert adds a set of hashes for the download queue for scheduling.` with `// Insert adds a set of hashes for the download queue for scheduling, returning`.

3. In `eth/sync.go`, the patch replaces `case downloader.ErrTimeout:` with `case downloader.ErrTimeout, downloader.ErrBadPeer:`.

4. In `eth/downloader/downloader.go`, the patch replaces `errBadPeer = errors.New("action from bad peer ignored")` with `ErrBadPeer = errors.New("action from bad peer ignored")`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue_test.go`, `eth/downloader/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue_test.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `peer`, `Insert`, and `queue`.

## Before/After Behavior

Before the patch, `fetchHashes` inserted received hashes into the queue but did not learn whether any of them were new, and if no common hash had been found yet it continued requesting more hashes from the same peer. After the patch, `queue.Insert` returns a count of newly accepted hashes, and `fetchHashes` aborts with `ErrBadPeer` when a non-terminal batch produces `inserts == 0`. `eth/sync.go` then handles `ErrBadPeer` by removing the peer.

# Root Cause

The downloader accepted non-terminal hash responses without validating that they advanced local queue state. Because the queue insertion API did not report whether anything new was added, the caller could stay in a request/response loop with a peer that kept sending duplicate hashes.

## Walkthrough

1. `fetchHashes` begins sync by queuing the starting hash and requesting hashes from the selected peer.

2. When a batch arrives, the downloader checks the sender, rejects empty batches, and scans for a known/common hash to decide whether syncing is complete.

3. In the old code, it called `d.queue.Insert(hashPack.hashes)` and, if `done` was still false, immediately requested more hashes from the same peer.

4. The patch changes `queue.Insert` to return how many hashes were actually new to the queue.

5. `fetchHashes` now stores that return value in `inserts` and returns `ErrBadPeer` when `inserts == 0 && !done`.

6. If the batch is non-terminal and does add something new, syncing continues as before.

7. `eth/sync.go` now treats `ErrBadPeer` like `ErrTimeout` and removes the offending peer.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 219 | hash synchronisation loop now enforces forward progress and returns `ErrBadPeer` on repeated non-advancing hash batches |
| eth/downloader/queue.go | 112 | queue insertion path now counts newly accepted hashes so the caller can detect replayed or duplicate-only responses |
| eth/sync.go | 82 | protocol manager treats `ErrBadPeer` like a timeout and disconnects the offending peer |

## Code Snippets

## Snippet 1

Context: `eth/downloader/downloader.go:267` (changes bounds, limits, or capacity handling)

Before
```go
}
			}
			d.queue.Insert(hashPack.hashes)

			if !done {
				activePeer.getHashes(hash)
				continue
```
After
```go
}
			}
			// Insert all the new hashes, but only continue if got something useful
			inserts := d.queue.Insert(hashPack.hashes)
			if inserts == 0 && !done {
				return ErrBadPeer
			} else if !done {
				activePeer.getHashes(hash)
```

## Snippet 2

Context: `eth/downloader/queue.go:123` (changes signature or replay validation logic)

Before
```go
}

// Insert adds a set of hashes for the download queue for scheduling.
func (q *queue) Insert(hashes []common.Hash) {
	q.lock.Lock()
	defer q.lock.Unlock()

	// Insert all the hashes prioritized in the arrival order
```
After
```go
}

// Insert adds a set of hashes for the download queue for scheduling, returning
// the number of new hashes encountered.
func (q *queue) Insert(hashes []common.Hash) int {
	q.lock.Lock()
	defer q.lock.Unlock()
```

## Snippet 3

Context: `eth/sync.go:102` (changes bounds, limits, or capacity handling)

Before
```go
glog.V(logger.Debug).Infof("Synchronisation already in progress")

	case downloader.ErrTimeout:
		glog.V(logger.Debug).Infof("Removing peer %v due to sync timeout", peer.id)
		pm.removePeer(peer)
	case downloader.ErrPendingQueue:
		glog.V(logger.Debug).Infoln("Synchronisation aborted:", err)
	default:
```
After
```go
glog.V(logger.Debug).Infof("Synchronisation already in progress")

	case downloader.ErrTimeout, downloader.ErrBadPeer:
		glog.V(logger.Debug).Infof("Removing peer %v: %v", peer.id, err)
		pm.removePeer(peer)

	case downloader.ErrPendingQueue:
		glog.V(logger.Debug).Infoln("Synchronisation aborted:", err)
```

## Snippet 4

Context: `eth/downloader/downloader.go:28` (changes a sensitive control or state-update path)

Before
```go
ErrBusy                = errors.New("busy")
	errUnknownPeer         = errors.New("peer's unknown or unhealthy")
	errBadPeer             = errors.New("action from bad peer ignored")
	errNoPeers             = errors.New("no peers to keep download active")
	ErrPendingQueue        = errors.New("pending items in queue")
```
After
```go
ErrBusy                = errors.New("busy")
	errUnknownPeer         = errors.New("peer's unknown or unhealthy")
	ErrBadPeer             = errors.New("action from bad peer ignored")
	errNoPeers             = errors.New("no peers to keep download active")
	ErrPendingQueue        = errors.New("pending items in queue")
```

# Fix Pattern

Expose whether untrusted input made forward progress, reject zero-progress non-terminal responses, and propagate that failure into peer removal.

## How It Was Fixed

The fix changed `queue.Insert` to return a new-hash count, used that count in `fetchHashes` to detect duplicate-only non-terminal responses, and promoted `ErrBadPeer` into the synchronisation error handling so the peer is removed.

# Why It Matters

1. The changed path consumes data from remote peers during sync.

2. Without a progress check, a peer could keep the downloader busy without advancing state.

3. The fix turns a silent stall condition into an explicit bad-peer outcome.

4. Peer removal limits repeated abuse from the same source.

# Evidence Notes

The strongest evidence is the new `inserts := d.queue.Insert(hashPack.hashes)` check in `eth/downloader/downloader.go` and the new `if inserts == 0 && !done { return ErrBadPeer }` branch. `eth/downloader/queue.go` was changed specifically so `Insert` returns the number of new hashes encountered. `eth/sync.go` was updated to remove peers on `downloader.ErrBadPeer`. The code supports a downloader progress-validation fix and a denial-of-service/resource-waste theory; it does not support stronger claims such as consensus failure, invalid block acceptance, or quantified impact. Protocol security invariant: During downloader hash synchronisation, each non-terminal peer response must contribute at least one previously unseen hash until a known/common hash is reached. A peer that only returns already-known or already-queued hashes is violating the progress requirement and should not be kept in the sync loop. Verification notes: The patch shows a peer can stall or waste downloader work; it does not prove full node compromise. The evidence supports denial-of-service style impact, not consensus corruption or invalid-block acceptance. The patch does not quantify whether the attack is CPU-bound, memory-bound, bandwidth-bound, or how severe it is in practice. The diff does not prove exploitability beyond the sync/download path or across all protocol versions. The provided diff shows the control-flow change that rejects zero-progress non-terminal batches. The provided diff shows the queue API change that makes zero-progress detectable. The provided diff shows peer removal on `ErrBadPeer`. The evidence does not quantify resource consumption or show a proof-of-concept attack trace. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The patch shows a concrete fix for malicious peer behavior in a network-exposed downloader path. Before the change, a peer could keep returning duplicate-only non-terminal hash batches and the node would continue requesting more data without making progress. After the change, zero-progress responses are detected, converted into `ErrBadPeer`, and the peer is removed. That is strong patch-level evidence for a remote denial-of-service/resource-exhaustion security fix, not just routine reliability cleanup.

## Security Evidence

1. The affected code processes hash responses from remote peers during synchronization.
2. `queue.Insert` was changed to report how many hashes were actually new, enabling detection of duplicate-only responses.
3. `fetchHashes` now returns `ErrBadPeer` when a non-terminal batch adds zero new hashes (`inserts == 0 && !done`).
4. `eth/sync.go` was updated to remove peers that trigger `ErrBadPeer`, cutting off the abusive source.
5. The commit subject explicitly frames the issue as an attack: `prevent hash repeater attack`.

## Missing Evidence

1. The patch does not quantify CPU, bandwidth, or memory impact.
2. No exploit trace or test case is shown proving end-to-end denial of service.
3. The diff does not establish scope across protocol versions or deployment conditions.

## Claim Boundaries

1. This supports a downloader-path remote DoS/resource-waste fix caused by malicious peers.
2. It does not support claims about consensus failure, invalid block acceptance, or key/cryptographic compromise.
3. Severity and exact exploitability are not proven beyond the observed zero-progress request loop.
