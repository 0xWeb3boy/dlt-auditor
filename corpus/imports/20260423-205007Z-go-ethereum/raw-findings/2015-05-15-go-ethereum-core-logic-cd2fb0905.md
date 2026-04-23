---
case_id: case_20150515_cd2fb0905
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
bug_class: p2p-sync-no-progress-dos
impact_type:
  - denial-of-service
tags:
  - blockchain-core
  - p2p
  - sync
  - duplicate-hash-replay
  - bad-peer-eviction
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch prevents a peer from repeatedly sending only hashes already known to the downloader queue during hash synchronization. The fix makes queue insertion report forward progress and treats a non-final zero-progress hash batch as ErrBadPeer, which the sync manager then removes.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `d.queue.Insert(hashPack.hashes)` with `// Insert all the new hashes, but only continue if got something useful`.

2. In `eth/downloader/queue.go`, the patch replaces `// Insert adds a set of hashes for the download queue for scheduling.` with `// Insert adds a set of hashes for the download queue for scheduling, returning`.

3. In `eth/sync.go`, the patch replaces `case downloader.ErrTimeout:` with `case downloader.ErrTimeout, downloader.ErrBadPeer:`.

4. In `eth/downloader/downloader.go`, the patch replaces `errBadPeer = errors.New("action from bad peer ignored")` with `ErrBadPeer = errors.New("action from bad peer ignored")`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue_test.go`, `eth/downloader/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue_test.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `peer`, `Insert`, and `queue`.

## Before/After Behavior

Before the patch, fetchHashes inserted a non-empty hash batch and continued asking the same peer for more hashes whenever no common block had been reached, even if the batch only repeated hashes already in the queue. After the patch, queue.Insert returns the count of newly added hashes; fetchHashes returns ErrBadPeer when a non-terminal batch adds zero new hashes, and eth/sync.go removes peers that cause ErrBadPeer.

# Root Cause

The hash synchronization loop accepted any non-empty peer response as enough to continue, while the queue insertion API did not expose whether the response actually advanced queue state. This left duplicate-only responses from a peer unchecked before synchronization reached a terminal/common-hash condition.

## Walkthrough

1. fetchHashes receives a hash batch from the active peer and verifies the peer id.

2. It rejects empty hash sets and scans the batch for a known or already queued block to determine whether hash fetching is done.

3. Before the fix, it inserted the batch without knowing whether any hashes were new.

4. If not done, it requested another hash batch from the same peer even after a duplicate-only batch.

5. The fixed queue.Insert skips already known hashes and returns the number of newly inserted hashes.

6. The fixed fetchHashes returns ErrBadPeer when inserts == 0 and the sync is not done.

7. ProtocolManager handles ErrBadPeer like a timeout and removes the peer.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 219 | hash synchronization loop that validates active peer responses and rejects zero-progress repeated hash batches |
| eth/downloader/queue.go | 123 | download queue insertion now counts newly encountered hashes instead of silently accepting duplicates |
| eth/sync.go | 102 | sync error handling removes peers classified as bad by the downloader |
| eth/downloader/downloader.go | 28 | ErrBadPeer is exported so the sync manager can act on downloader peer rejection |

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

Expose forward-progress information from queue mutation and enforce it at the peer-controlled protocol loop boundary before issuing more work to the same peer.

## How It Was Fixed

queue.Insert was changed from a void method to returning the number of new hashes inserted. fetchHashes now checks that count and rejects non-terminal zero-insert batches with ErrBadPeer. ErrBadPeer was exported so eth/sync.go can remove the offending peer.

# Why It Matters

1. Prevents peer-controlled duplicate hash batches from keeping synchronization in a no-progress loop.

2. Allows the downloader to distinguish useful hash responses from repeated data.

3. Connects downloader bad-peer detection to peer removal.

4. The evidence does not support claims of block validation bypass, hash collision failure, memory corruption, or quantified resource exhaustion.

# Evidence Notes

The strongest evidence is the fetchHashes change in eth/downloader/downloader.go, the queue.Insert return-value change in eth/downloader/queue.go, the ErrBadPeer export, and eth/sync.go removing peers on ErrBadPeer. The commit subject explicitly says "prevent hash repeater attack". The supported claim is a peer-driven hash-sync replay/no-progress vulnerability, not a broader consensus or cryptographic failure. Protocol security invariant: During downloader hash synchronization, a non-terminal response from the active peer must contribute at least one previously unseen hash to the queue before the downloader requests more hashes from that peer. Verification notes: The patch does not show remote code execution or memory corruption. The patch does not prove invalid blocks or chain state could be accepted. The patch does not involve cryptographic hash collision resistance being broken. The patch does not quantify the resource impact of the repeater behavior. The patch only supports a peer-driven sync no-progress or resource-control issue. Code evidence shows zero newly inserted hashes now causes ErrBadPeer only when synchronization is not done. sync.go evidence shows ErrBadPeer leads to peer removal. No provided evidence quantifies resource impact or shows invalid chain acceptance. No commands, tests, or external context were used. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `p2p-sync-no-progress-dos`
Final impact type: `denial-of-service`
Final tags: `blockchain-core, p2p, sync, duplicate-hash-replay, bad-peer-eviction, denial-of-service`

The supplied evidence supports retaining this as a security fix. The commit subject explicitly frames the change as preventing a hash repeater attack, and the patch adds forward-progress validation for peer-controlled hash batches during synchronization. Duplicate-only non-terminal responses now return ErrBadPeer, and the protocol manager removes that peer, which directly mitigates a malicious peer causing repeated no-progress sync work.

## Security Evidence

1. Commit subject says "prevent hash repeater attack".
2. Downloader now checks the number of newly inserted hashes from a peer response.
3. A non-terminal batch with zero new hashes now returns ErrBadPeer.
4. ErrBadPeer is exported and handled by removing the peer from synchronization.
5. The affected path processes peer-supplied hashes in the blockchain synchronization protocol.

## Missing Evidence

1. No quantified CPU, bandwidth, memory, or availability impact is shown.
2. No evidence of consensus failure, invalid block acceptance, or cryptographic break is shown.
3. No exploit demonstration or test case is included in the supplied evidence.

## Claim Boundaries

1. Supported claim is limited to peer-driven duplicate-hash replay/no-progress behavior during sync.
2. Supported impact is denial-of-service or sync disruption, not chain integrity compromise.
3. The patch supports security-fix classification because it rejects and disconnects malicious peer behavior, but not broader cryptographic or consensus claims.
