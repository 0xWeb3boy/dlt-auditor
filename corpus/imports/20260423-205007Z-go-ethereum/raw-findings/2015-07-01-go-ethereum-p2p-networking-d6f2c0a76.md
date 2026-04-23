---
case_id: case_20150701_d6f2c0a76
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

The patch fixes a denial-of-service risk in go-ethereum's downloader hash-fetch path. It adds `maxQueuedHashes = 256 * 1024` with an explicit DOS-protection comment and changes `fetchHashes` so continuation depends on `d.queue.Pending() < maxQueuedHashes` instead of always continuing after a successful hash insert.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `// Notify the block fetcher of new hashes, and continue fetching` with `// Notify the block fetcher of new hashes, but stop if queue is full`.

2. In `eth/downloader/downloader.go`, the patch replaces `maxBannedHashes = 4096 // Number of bannable hashes before phasing old ones out` with `maxQueuedHashes = 256 * 1024 // Maximum number of hashes to queue for import (DOS pro...`.

3. In `eth/handler.go`, the patch replaces `glog.V(logger.Debug).Infof("%v: peer connected", p)` with `glog.V(logger.Debug).Infof("%v: peer connected [%s]", p, p.Name())`.

4. In `eth/downloader/downloader.go`, the patch adds `glog.V(logger.Detail).Infof("%v: inserting %d hashes from #%d", p, len(hashPack.hashe...`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `eth/downloader/queue.go`, `eth/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `queue`, `Number`, and `peer`.

## Before/After Behavior

Before the patch, `fetchHashes` inserted peer-provided hashes and then always notified `d.processCh` with `true`, continuing hash fetching in the shown path regardless of pending queue depth. After the patch, it computes whether the pending hash queue is below `maxQueuedHashes`, sends that continuation value, and returns when the queue has reached the cap. The `eth/handler.go` change only adds peer name information to debug logging.

# Root Cause

The hash-fetch loop's continuation decision was not tied to pending hash queue depth. After accepting a valid batch, the downloader continued requesting additional batches without the newly added cap check in this path.

## Walkthrough

1. `fetchHashes` requests hash batches from an active peer with `p.getAbsHashes(from, MaxHashFetch)`.

2. When hashes arrive, the function checks that they came from the active peer and inserts them into `d.queue`.

3. If insertion fails to include the full batch, the peer is treated as bad and the path aborts.

4. Before the fix, successful insertion led to `d.processCh <- true`, so fetching continued unconditionally in the shown code.

5. The patch introduces `maxQueuedHashes` as a maximum queued-hash limit for DOS protection.

6. After insertion, the code evaluates `cont := d.queue.Pending() < maxQueuedHashes`.

7. The downloader sends `cont` to `d.processCh` and returns when `cont` is false, stopping further hash fetching once the queue is full.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 35 | defines maxQueuedHashes as the downloader hash queue cap for DOS protection |
| eth/downloader/downloader.go | 820 | checks pending hash queue depth after inserting peer-provided hashes and stops further hash fetching when the cap is reached |
| eth/handler.go | 165 | diagnostic logging change only; no security-relevant behavior shown |

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

Add resource admission control to a remotely driven queueing path by checking queue depth before continuing to request more work.

## How It Was Fixed

The fix defines a maximum pending hash queue size and replaces unconditional continuation with a queue-depth-based continuation decision. If `d.queue.Pending()` is no longer below `maxQueuedHashes`, `fetchHashes` stops instead of fetching another batch.

# Why It Matters

1. Limits remote peer influence over downloader memory and queued work.

2. Prevents continued hash fetching after the pending queue reaches the configured cap.

3. Keeps the claim scoped to DOS/resource exhaustion in hash queueing.

4. Does not imply code execution, consensus failure, or peer banning.

# Evidence Notes

The strongest evidence is the commit subject naming a DOS vulnerability in hash queueing, the new `maxQueuedHashes` constant marked `DOS protection`, and the change from `d.processCh <- true` to a continuation value based on `d.queue.Pending()`. The evidence supports a resource-exhaustion security fix. It does not establish a specific crash threshold, exploit procedure, or broader protocol compromise. The handler logging change is ancillary. Protocol security invariant: During eth synchronization, remotely supplied hash batches must not cause the downloader's pending hash queue to grow past an explicit capacity limit; fetching should stop once queued hash work reaches that limit. Verification notes: The patch shows prevention of unbounded hash queue growth, not arbitrary remote code execution or consensus compromise. The evidence does not prove a specific memory exhaustion threshold or crash condition beyond excessive queued hashes/work. The patch does not show peer banning or punishment for filling the queue; it only stops further fetching in this path. The logging-only handler change should not be treated as part of the vulnerability fix. Verified from provided evidence only; no external files or commands used. Security classification is supported by explicit commit language and in-code DOS-protection comment. Claims are limited to bounded hash queue continuation in `fetchHashes`. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied evidence supports retaining this as a security fix. The commit subject explicitly identifies a DOS vulnerability in hash queueing, and the patch adds a hard cap labeled DOS protection to a peer-driven hash download path. The behavioral change replaces unconditional continued fetching with a queue-depth check and exits when the pending hash queue reaches the cap, which directly addresses resource exhaustion risk.

## Security Evidence

1. Commit subject says: DOS vulnerability in hash queueing.
2. Patch adds maxQueuedHashes with an in-code comment: Maximum number of hashes to queue for import (DOS protection).
3. fetchHashes handles hashes supplied by an active peer and inserts them into the downloader queue.
4. Continuation changes from always sending true to sending d.queue.Pending() < maxQueuedHashes.
5. The function returns when the queue is full, stopping further hash fetching in this path.

## Missing Evidence

1. No exploit procedure or concrete crash threshold is shown.
2. No test evidence is supplied demonstrating memory exhaustion before the fix.
3. No evidence shows broader consensus compromise or arbitrary code execution.

## Claim Boundaries

1. Scope should remain limited to denial-of-service/resource exhaustion through downloader hash queue growth.
2. The handler logging change is ancillary and should not be treated as security-relevant.
3. The patch shows stopping further fetching, not peer punishment or banning.
4. The evidence supports remote peer influence over queued work, but not impacts beyond availability/resource exhaustion.
