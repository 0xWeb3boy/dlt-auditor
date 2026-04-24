---
case_id: case_20150701_d6f2c0a76
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
bug_class: resource-exhaustion
impact_type:
  - remote-dos
confidence: medium
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
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a likely denial-of-service fix in the downloader hash-queueing path. Before the change, `fetchHashes` kept signaling continuation after inserting each batch. The patch adds `maxQueuedHashes` and makes continuation depend on `d.queue.Pending() < maxQueuedHashes`, stopping further fetches when the queue is full.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `// Notify the block fetcher of new hashes, and continue fetching` with `// Notify the block fetcher of new hashes, but stop if queue is full`.

2. In `eth/downloader/downloader.go`, the patch replaces `maxBannedHashes = 4096 // Number of bannable hashes before phasing old ones out` with `maxQueuedHashes = 256 * 1024 // Maximum number of hashes to queue for import (DOS pro...`.

3. In `eth/handler.go`, the patch replaces `glog.V(logger.Debug).Infof("%v: peer connected", p)` with `glog.V(logger.Debug).Infof("%v: peer connected [%s]", p, p.Name())`.

4. In `eth/downloader/downloader.go`, the patch adds `glog.V(logger.Detail).Infof("%v: inserting %d hashes from #%d", p, len(hashPack.hashe...`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `eth/downloader/queue.go`, `eth/peer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/downloader_test.go`. The strongest project-level identifiers around this patch are `hashes`, `queue`, `Number`, and `peer`.

## Before/After Behavior

Before the patch, `fetchHashes` inserted each received hash batch and then unconditionally notified the processing path with `d.processCh <- true`, with the adjacent comment saying to continue fetching. After the patch, it defines `maxQueuedHashes = 256 * 1024`, computes `cont := d.queue.Pending() < maxQueuedHashes`, sends `cont` instead of a hard-coded `true`, and returns when `cont` is false so the loop stops fetching more hashes once the pending queue reaches the limit.

# Root Cause

The hash fetch loop lacked an explicit bound on pending queued hashes and continued requesting more peer-supplied hashes without checking whether the backlog was already too large.

## Walkthrough

1. `fetchHashes` receives a peer hash batch from `d.hashCh` and inserts it into `d.queue`.

2. In the pre-patch code, the next signal was always `d.processCh <- true`, so the fetch side kept continuing after each batch.

3. The patch introduces `maxQueuedHashes = 256 * 1024` with a `DOS protection` comment.

4. After insertion, the patched code computes `cont := d.queue.Pending() < maxQueuedHashes`.

5. The signal sent on `d.processCh` changes from unconditional `true` to `cont`.

6. The changed lines include `if !cont { return nil }`, so fetching stops once the pending queue is full.

7. The `eth/handler.go` change is only a logging adjustment and does not support the vulnerability claim.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 35 | Introduces the global backlog cap `maxQueuedHashes` as the queueing safety bound. |
| eth/downloader/downloader.go | 775 | ETH hash-download loop that receives peer hash batches and inserts them into the sync queue. |
| eth/downloader/downloader.go | 813 | Post-insert admission/control point: now computes `cont := d.queue.Pending() < maxQueuedHashes` and stops further fetching when backlog is full. |
| eth/handler.go | 165 | Ancillary peer-connection logging change; not part of the security fix. |

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

Add an explicit queue-depth cap and gate continuation of a peer-driven fetch loop on the current pending backlog.

## How It Was Fixed

The fix adds a downloader-wide backlog threshold, `maxQueuedHashes`, and uses it in `fetchHashes` after queue insertion. Instead of always continuing, the code checks the current pending count, forwards that boolean to the processing path, and exits the fetch loop when the queue has reached the configured limit.

# Why It Matters

1. Prevents continued hash fetching when queued work is already at the configured ceiling.

2. Makes the resource-control limit explicit in the downloader path.

3. Supports a denial-of-service mitigation claim, but not stronger claims such as consensus failure or invalid-block acceptance.

# Evidence Notes

The strongest evidence is in `eth/downloader/downloader.go`: a new constant `maxQueuedHashes = 256 * 1024 // Maximum number of hashes to queue for import (DOS protection)` and the `fetchHashes` control-flow change from unconditional continuation to `cont := d.queue.Pending() < maxQueuedHashes` plus an early return when the queue is full. This supports a queue-bounding DoS fix in the downloader. The `eth/handler.go` hunk only changes debug logging. The evidence does not establish the exact exhausted resource, the full exploit conditions, or any consensus-impacting behavior. Protocol security invariant: The downloader must keep peer-driven hash backlog bounded during sync and stop requesting more hashes once pending queued work reaches a fixed limit. Verification notes: The patch shows DoS/resource-exhaustion mitigation, not code execution or privilege escalation. The evidence does not quantify whether the exhaustion was memory-only, CPU-only, or both. The patch does not prove consensus corruption or acceptance of invalid blocks. The diff does not show whether one peer alone could fully exhaust the node or only degrade sync performance. The logging change in `eth/handler.go` is not evidence of a security behavior change. The code clearly adds a fixed pending-hash limit in the downloader path. The code clearly changes continuation from unconditional to queue-depth-dependent. The evidence supports a DoS/resource-exhaustion interpretation, but not a stronger proof than likely. The logging change in `eth/handler.go` should be excluded from the security rationale. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The patch is plausibly security-relevant and worth keeping, but the code evidence is stronger for hardening than for a fully proven exploitable vulnerability. The downloader previously kept fetching peer-supplied hashes without a visible backlog cap, and the change adds an explicit `maxQueuedHashes` limit labeled as DOS protection and stops continued fetching once the pending queue is full. That strongly supports a remote resource-exhaustion mitigation in a network-facing path, even though the diff alone does not prove exact exploitability, impact magnitude, or whether a single peer could reliably take down a node.

## Security Evidence

1. Commit subject explicitly says it fixes a DOS vulnerability in hash queueing.
2. A new `maxQueuedHashes` limit is added with the comment `DOS protection`.
3. The fetch loop changes from unconditional continuation to `cont := d.queue.Pending() < maxQueuedHashes`.
4. The patched logic returns when the queue is full, preventing further peer-driven hash accumulation.
5. The affected code is in the p2p/downloader path that processes remote peer data.

## Missing Evidence

1. The diff does not show the exact resource exhausted, such as memory or CPU.
2. The patch alone does not prove a complete end-to-end denial of service against a node.
3. It is not shown whether one malicious peer is sufficient to trigger the condition in practice.
4. No test or reproduction is provided in the supplied evidence.

## Claim Boundaries

1. Supported claim: the patch adds a queue-depth bound to reduce DOS risk in peer-driven hash fetching.
2. Supported claim: this is security-relevant hardening for resource-control in a network-facing path.
3. Not supported from the patch alone: guaranteed remote node crash or full service outage.
4. Not supported from the patch alone: broader impacts such as consensus failure, invalid block acceptance, or code execution.
