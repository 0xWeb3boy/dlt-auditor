---
case_id: case_20150515_cd2fb09051
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
confidence: high
source_quality: high
date: 2015-05-15
source_refs:
  - git:cd2fb0905109828028172c84f9c10f1343647ca6
  - "eth/downloader/downloader.go:267"
  - "eth/downloader/queue.go:123"
  - "eth/sync.go:102"
  - "eth/downloader/downloader.go:28"
bug_class: duplicate-hash-replay
impact_type:
  - sync-denial-of-service
tags:
  - blockchain-core
  - p2p
  - downloader
  - duplicate-detection
  - peer-removal
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a hash-repetition weakness in go-ethereum's ETH downloader. It makes queue insertion report how many hashes were actually new, then rejects a peer when a non-final hash response contributes zero new queue entries. The outer sync layer handles that bad-peer result by removing the peer.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `d.queue.Insert(hashPack.hashes)` with `// Insert all the new hashes, but only continue if got something useful`.

2. In `eth/downloader/queue.go`, the patch replaces `// Insert adds a set of hashes for the download queue for scheduling.` with `// Insert adds a set of hashes for the download queue for scheduling, returning`.

3. In `eth/sync.go`, the patch replaces `case downloader.ErrTimeout:` with `case downloader.ErrTimeout, downloader.ErrBadPeer:`.

4. In `eth/downloader/downloader.go`, the patch replaces `errBadPeer = errors.New("action from bad peer ignored")` with `ErrBadPeer = errors.New("action from bad peer ignored")`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue_test.go`, `eth/downloader/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue_test.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `peer`, `Insert`, and `queue`.

## Before/After Behavior

Before the patch, `fetchHashes` inserted returned hashes into the queue and continued requesting more hashes whenever the common-hash condition had not been reached, without knowing whether the response added anything new. After the patch, `queue.Insert` returns the number of newly encountered hashes; `fetchHashes` returns `ErrBadPeer` when that count is zero and the fetch is not done, and `eth/sync.go` removes peers that cause `ErrBadPeer`.

# Root Cause

The downloader treated non-empty hash responses as progress even when all returned hashes were duplicates already tracked by the queue. That allowed a peer to keep the hash-fetch loop active without advancing synchronization.

## Walkthrough

1. `ProtocolManager.synchronise` calls `pm.downloader.Synchronise(peer.id, peer.recentHash)` for ETH synchronization.

2. The downloader requests hashes from the active peer and receives `hashPack.hashes` in `fetchHashes`.

3. The code verifies the response peer, rejects empty hash sets, and scans for a known or already downloaded block to decide whether hash fetching is done.

4. Before the fix, the remaining hashes were inserted without reporting whether any were new, and the downloader continued when `done` was false.

5. A peer returning only duplicate hashes could therefore trigger another request while contributing no new queued work.

6. After the fix, `queue.Insert` counts newly encountered hashes and returns that count.

7. If no new hashes were inserted and the phase is not done, `fetchHashes` returns `ErrBadPeer`.

8. The sync layer now treats `downloader.ErrBadPeer` like a timeout and removes the peer.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 267 | Detects zero-progress hash responses during fetchHashes and returns ErrBadPeer when repeated hashes do not complete synchronization. |
| eth/downloader/queue.go | 123 | Changes queue Insert to report the number of newly encountered hashes so callers can distinguish progress from duplicate input. |
| eth/sync.go | 102 | Treats ErrBadPeer like a timeout by removing the misbehaving peer from the protocol manager. |
| eth/downloader/downloader.go | 28 | Exports ErrBadPeer so the sync layer can observe and act on the downloader's bad-peer classification. |

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

Expose progress at the queue boundary and enforce it at the protocol loop boundary.

## How It Was Fixed

`eth/downloader/queue.go` changed `Insert` from a void method to one returning the number of new hashes. `eth/downloader/downloader.go` checks that return value and returns exported `ErrBadPeer` on zero-progress non-final responses. `eth/sync.go` matches `downloader.ErrBadPeer` and removes the peer.

# Why It Matters

1. Prevents duplicate-only hash batches from being treated as useful sync input.

2. Stops a peer from keeping the hash-fetch loop active without making progress.

3. Bounds the security claim to peer-level synchronization stalling or denial of service.

4. The evidence does not support claims of cryptographic bypass, remote code execution, or consensus failure.

# Evidence Notes

The strongest evidence is the focused change in `fetchHashes`: `d.queue.Insert(hashPack.hashes)` became `inserts := d.queue.Insert(hashPack.hashes)`, followed by `if inserts == 0 && !done { return ErrBadPeer }`. Supporting evidence is the `queue.Insert` contract change to return the number of new hashes and the sync-layer change that removes peers on `downloader.ErrBadPeer`. The commit subject explicitly states `prevent hash repeater attack`, and the code change directly implements duplicate-response detection and peer removal. Protocol security invariant: During ETH synchronization, a peer's hash response must either advance the downloader by adding new hashes to the queue or reach the known/common-hash condition that completes hash fetching. Duplicate-only responses should not keep the sync loop active or preserve the peer as usable. Verification notes: The patch does not prove remote code execution or consensus violation. The patch does not show forged hashes bypassing cryptographic validation. The patch does not quantify resource exhaustion impact or attack cost. The patch only supports a peer-level synchronization denial-of-service or stalling interpretation from repeated hashes. Evidence supports a security fix for duplicate hash replay or sync non-progress. Impact should remain described as synchronization stalling or denial of service; broader exploit claims are unsupported. Helper/API changes in `queue.go` are support code for the downloader decision, not an independent root cause. No evidence in the provided input quantifies resource exhaustion severity or attack cost. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `duplicate-hash-replay`
Final impact type: `sync-denial-of-service`
Final tags: `blockchain-core, p2p, downloader, duplicate-detection, peer-removal, denial-of-service`

The supplied evidence supports keeping this as a security fix. The commit subject explicitly describes preventing a hash repeater attack, and the patch changes downloader behavior so duplicate-only hash responses from a peer no longer keep synchronization progressing indefinitely. The fix adds progress accounting to queue insertion, returns ErrBadPeer on zero-progress non-final responses, and removes that peer at the sync layer. The supported impact is bounded to peer-driven sync stalling or denial of service, not cryptographic compromise or consensus failure.

## Security Evidence

1. Commit subject says "prevent hash repeater attack".
2. Downloader now checks how many hashes were newly inserted before requesting more hashes.
3. A non-final response with zero new hashes returns ErrBadPeer.
4. Sync layer removes peers that trigger downloader.ErrBadPeer.
5. The changed path processes peer-supplied hash data during ETH synchronization.

## Missing Evidence

1. No exploit demonstration or severity measurement is provided.
2. No evidence supports remote code execution, fund loss, or consensus violation.
3. No proof is shown that the issue affects honest peers beyond malicious or faulty peer behavior.

## Claim Boundaries

1. Classify as duplicate hash replay causing synchronization non-progress or denial of service.
2. Do not claim cryptographic validation bypass.
3. Do not claim chain consensus corruption.
4. Do not treat queue.Insert API changes as an independent vulnerability.
