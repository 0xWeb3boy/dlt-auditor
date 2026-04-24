---
case_id: case_20150701_d6f2c0a76f
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
bug_class: resource-exhaustion
impact_type:
  - remote-dos
confidence: high
source_quality: medium
tags:
  - blockchain-core
  - p2p-networking
  - resource-exhaustion
  - remote-dos
  - p2p
  - queue
date: 2015-07-01
source_refs:
  - git:d6f2c0a76f6635ebeb245815c5f686c545ed527d
  - "eth/downloader/downloader.go:820"
  - "eth/downloader/downloader.go:35"
  - "eth/handler.go:165"
  - "eth/downloader/downloader.go:813"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a denial-of-service/resource-exhaustion issue in go-ethereum's eth downloader hash queue. In `fetchHashes`, the downloader previously continued requesting more hashes after each fully accepted batch. The patch adds `maxQueuedHashes = 256 * 1024` with a DOS-protection comment and changes continuation to depend on `d.queue.Pending() < maxQueuedHashes`, returning when the queue is full. The `eth/handler.go` change is only debug logging and is not part of the security fix.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `// Notify the block fetcher of new hashes, and continue fetching` with `// Notify the block fetcher of new hashes, but stop if queue is full`.

2. In `eth/downloader/downloader.go`, the patch replaces `maxBannedHashes = 4096 // Number of bannable hashes before phasing old ones out` with `maxQueuedHashes = 256 * 1024 // Maximum number of hashes to queue for import (DOS pro...`.

3. In `eth/handler.go`, the patch replaces `glog.V(logger.Debug).Infof("%v: peer connected", p)` with `glog.V(logger.Debug).Infof("%v: peer connected [%s]", p, p.Name())`.

4. In `eth/downloader/downloader.go`, the patch adds `glog.V(logger.Detail).Infof("%v: inserting %d hashes from #%d", p, len(hashPack.hashe...`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `eth/downloader/queue.go`, `eth/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `queue`, `Number`, and `peer`.

## Before/After Behavior

Before the patch, after a non-empty hash batch was inserted successfully, `fetchHashes` always sent `true` on `d.processCh` and proceeded to fetch another batch. The supplied evidence does not show any queue-depth check on that continuation path. After the patch, `fetchHashes` computes whether `d.queue.Pending()` is below `maxQueuedHashes`, sends that boolean on `d.processCh`, and returns instead of fetching more hashes when the pending queue reaches the limit.

# Root Cause

The hash-fetch continuation path lacked a visible admission-control check based on pending queue depth. Accepted hash batches from a peer could cause the downloader to keep requesting additional hashes even after the pending hash backlog had grown too large.

## Walkthrough

1. `fetchHashes` requests hash batches from an eth peer.

2. When a batch arrives, the downloader checks it came from the active peer and treats an empty batch as completion.

3. For non-empty batches, the downloader inserts the hashes into `d.queue` and rejects the peer if not all supplied hashes were inserted.

4. Before the fix, every fully inserted batch caused `d.processCh` to receive `true`, so fetching continued.

5. The patch introduces `maxQueuedHashes = 256 * 1024` as a maximum queued hash count for DOS protection.

6. The continuation decision is changed to `d.queue.Pending() < maxQueuedHashes`.

7. When the queue is at or above that limit, `fetchHashes` returns instead of requesting another batch.

8. The peer-name logging change in `eth/handler.go` is unrelated to this resource-control behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 35 | defines the maximum pending hash queue size used as DOS protection |
| eth/downloader/downloader.go | 820 | enforces hash-fetch admission control by stopping further hash requests when the pending queue reaches the limit |
| eth/handler.go | 165 | unrelated peer connection logging change |

## Code Snippets

## Snippet 1

Context: `eth/downloader/downloader.go:820` (changes bounds, limits, or capacity handling)

Before
```go
return errBadPeer
			}
			// Notify the block fetcher of new hashes, and continue fetching
			select {
			case d.processCh <- true:
			default:
			}
			from += uint64(len(hashPack.hashes))
```
After
```go
return errBadPeer
			}
			// Notify the block fetcher of new hashes, but stop if queue is full
			cont := d.queue.Pending() < maxQueuedHashes
			select {
			case d.processCh <- cont:
			default:
			}
```

## Snippet 2

Context: `eth/downloader/downloader.go:35` (changes a sensitive control or state-update path)

Before
```go
crossCheckCycle = time.Second      // Period after which to check for expired cross checks

	maxBannedHashes = 4096 // Number of bannable hashes before phasing old ones out
	maxBlockProcess = 256  // Number of blocks to import at once into the chain
)
```
After
```go
crossCheckCycle = time.Second      // Period after which to check for expired cross checks

	maxQueuedHashes = 256 * 1024 // Maximum number of hashes to queue for import (DOS protection)
	maxBannedHashes = 4096       // Number of bannable hashes before phasing old ones out
	maxBlockProcess = 256        // Number of blocks to import at once into the chain
)
```

## Snippet 3

Context: `eth/handler.go:165` (changes a sensitive control or state-update path)

Before
```go
// this function terminates, the peer is disconnected.
func (pm *ProtocolManager) handle(p *peer) error {
	glog.V(logger.Debug).Infof("%v: peer connected", p)

	// Execute the Ethereum handshake
```
After
```go
// this function terminates, the peer is disconnected.
func (pm *ProtocolManager) handle(p *peer) error {
	glog.V(logger.Debug).Infof("%v: peer connected [%s]", p, p.Name())

	// Execute the Ethereum handshake
```

## Snippet 4

Context: `eth/downloader/downloader.go:813` (changes a sensitive control or state-update path)

Before
```go
}
			// Otherwise insert all the new hashes, aborting in case of junk
			inserts := d.queue.Insert(hashPack.hashes, true)
			if len(inserts) != len(hashPack.hashes) {
```
After
```go
}
			// Otherwise insert all the new hashes, aborting in case of junk
			glog.V(logger.Detail).Infof("%v: inserting %d hashes from #%d", p, len(hashPack.hashes), from)

			inserts := d.queue.Insert(hashPack.hashes, true)
			if len(inserts) != len(hashPack.hashes) {
```

# Fix Pattern

Add bounded admission control to remote-supplied work before requesting more of it. Continue fetching only while pending queued work remains below a fixed limit.

## How It Was Fixed

The patch added the `maxQueuedHashes` constant and replaced the unconditional continuation signal with a queue-depth check. `fetchHashes` now sends the computed continuation value to `processCh` and stops the hash-fetch loop when the queue is full.

# Why It Matters

1. Remote peers supply hash batches to this downloader path.

2. Without a queue-depth gate, accepted batches could keep increasing local pending work.

3. The fix bounds the hash backlog using `maxQueuedHashes`.

4. The evidence supports denial-of-service/resource-exhaustion mitigation only.

5. The exact memory or CPU impact is not quantified by the supplied evidence.

# Evidence Notes

Primary evidence is the change in `eth/downloader/downloader.go` around `fetchHashes`, replacing `d.processCh <- true` with `cont := d.queue.Pending() < maxQueuedHashes` and returning when `cont` is false. Supporting evidence is the new `maxQueuedHashes = 256 * 1024` constant annotated as DOS protection. The commit subject explicitly identifies a DOS vulnerability in hash queueing. The added insertion log and the `eth/handler.go` peer-name log change are not security-relevant based on the provided evidence. Protocol security invariant: A remote eth peer supplying block hashes must not be allowed to drive the downloader into accumulating excessive pending hash work; hash fetching should stop once the pending hash queue reaches a fixed limit. Verification notes: The patch does not prove remote code execution, consensus corruption, or theft of funds. The evidence supports a denial-of-service/resource-exhaustion fix, not a broader protocol authentication flaw. The exact memory or CPU impact is not quantified by the patch. The handler logging change is not security-relevant on its own. Validated as a security fix because the commit message explicitly names a DOS vulnerability and the code adds queue-depth admission control. Classified as resource exhaustion because the changed behavior limits pending queued hashes. No evidence supports stronger claims such as code execution, consensus corruption, authentication bypass, or fund theft. No tests are provided in the input showing exploitability or exact resource impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied evidence supports retaining this as a security fix. The commit subject explicitly names a DOS vulnerability in hash queueing, and the patch adds a hard pending-hash queue limit annotated as DOS protection. The main behavioral change replaces unconditional continued hash fetching from a peer with a queue-depth check and returns once the queue is full, which directly addresses remote-driven resource exhaustion in the downloader path.

## Security Evidence

1. Commit subject says: DOS vulnerability in hash queueing.
2. Patch adds maxQueuedHashes with comment: Maximum number of hashes to queue for import (DOS protection).
3. fetchHashes previously continued after each accepted batch by sending true on processCh.
4. fetchHashes now computes cont from d.queue.Pending() < maxQueuedHashes and stops when the queue is full.
5. The affected path processes hash batches supplied by an eth peer.

## Missing Evidence

1. No exploit proof or test case is supplied.
2. Exact memory, CPU, or availability impact is not quantified.
3. The handler.go logging change is unrelated to the security behavior.

## Claim Boundaries

1. Supports denial-of-service/resource-exhaustion only.
2. Does not support claims of code execution, consensus failure, authentication bypass, or fund theft.
3. Security relevance is limited to bounding remote-supplied hash queue growth in the downloader.
