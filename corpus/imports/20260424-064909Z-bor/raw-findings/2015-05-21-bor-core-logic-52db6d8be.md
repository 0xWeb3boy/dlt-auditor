---
case_id: case_20150521_52db6d8be
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: high
date: 2015-05-21
source_refs:
  - git:52db6d8be577669bd5ba659ac223acf61956b05a
  - "eth/downloader/downloader.go:333"
  - "eth/downloader/downloader.go:324"
  - "eth/downloader/downloader.go:62"
  - "eth/downloader/downloader_test.go:526"
bug_class: verification-bypass
impact_type:
  - sync-integrity-bypass
confidence: medium
tags:
  - blockchain-core
  - downloader
  - peer-input
  - integrity-check
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch tightens `eth/downloader` cross-checking so a sampled block must match the exact expected parent, not just any parent already present in the download queue. The evidence supports a sync-path integrity bypass in downloader verification, with a regression test for the forged-parent case.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `for hash, deadline := range d.checks {` with `for hash, check := range d.checks {`.

2. In `eth/downloader/downloader.go`, the patch replaces `if _, ok := d.checks[block.Hash()]; ok {` with `if check, ok := d.checks[block.Hash()]; ok {`.

3. In `eth/downloader/downloader.go`, the patch replaces `mux *event.TypeMux` with `type crossCheck struct {`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Advanced form of the above forged blockchain attack, where not only does the`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `checks`, `block`, `hash`, and `check`.

## Before/After Behavior

Before the patch, pending cross-checks stored only a timeout, and sampled-block validation rejected a block only when its parent was absent from the queue. After the patch, each cross-check stores both expiry and an expected parent, and validation fails unless `block.ParentHash()` exactly equals that stored parent.

# Root Cause

The cross-check state was too weak: it remembered only expiration and later accepted any queued parent for a sampled block hash. That allowed the deferred verification step to test local membership rather than exact ancestry for the sampled block.

## Walkthrough

1. `d.checks` changed from `map[common.Hash]time.Time` to `map[common.Hash]*crossCheck`.

2. The new `crossCheck` struct adds a `parent` field alongside `expire`.

3. In `fetchHashes`, the old sampled-block check only tested whether `d.checks[block.Hash()]` existed and whether `d.queue.Has(block.ParentHash())`.

4. The new code loads the stored check object and rejects when `block.ParentHash() != check.parent`.

5. The timeout loop was updated from `deadline` to `check.expire`, showing the richer check state is now carried through the existing verification flow.

6. `TestMadeupParentBlockChainAttack` was added, and its comment explicitly describes forged parents that point to existing hashes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 59 | Cross-check state now stores both expiration and expected parent for sampled hashes. |
| eth/downloader/downloader.go | 318 | Core validation in `fetchHashes` now rejects sampled blocks whose parent does not exactly match the recorded parent. |
| eth/downloader/downloader.go | 333 | Cross-check timeout loop updated to use the richer cross-check object while preserving expiry enforcement. |
| eth/downloader/downloader_test.go | 526 | Regression test for forged blockchain attack using made-up parents that previously could evade the weaker check. |

## Code Snippets

## Snippet 1

Context: `eth/downloader/downloader.go:333` (changes signature or replay validation logic)

Before
```go
case <-crossTicker.C:
			// Iterate over all the cross checks and fail the hash chain if they're not verified
			for hash, deadline := range d.checks {
				if time.Now().After(deadline) {
					glog.V(logger.Debug).Infof("Cross check timeout for %x", hash)
					return ErrCrossCheckFailed
```
After
```go
case <-crossTicker.C:
			// Iterate over all the cross checks and fail the hash chain if they're not verified
			for hash, check := range d.checks {
				if time.Now().After(check.expire) {
					glog.V(logger.Debug).Infof("Cross check timeout for %x", hash)
					return ErrCrossCheckFailed
```

## Snippet 2

Context: `eth/downloader/downloader.go:324` (changes signature or replay validation logic)

Before
```go
}
			block := blockPack.blocks[0]
			if _, ok := d.checks[block.Hash()]; ok {
				if !d.queue.Has(block.ParentHash()) {
					return ErrCrossCheckFailed
				}
```
After
```go
}
			block := blockPack.blocks[0]
			if check, ok := d.checks[block.Hash()]; ok {
				if block.ParentHash() != check.parent {
					return ErrCrossCheckFailed
				}
```

## Snippet 3

Context: `eth/downloader/downloader.go:62` (changes signature or replay validation logic)

Before
```go
}

type Downloader struct {
	mux *event.TypeMux

	mu     sync.RWMutex
	queue  *queue                    // Scheduler for selecting the hashes to download
	peers  *peerSet                  // Set of active peers from which download can proceed
```
After
```go
}

type crossCheck struct {
	expire time.Time
	parent common.Hash
}

type Downloader struct {
```

## Snippet 4

Context: `eth/downloader/downloader_test.go:526` (changes signature or replay validation logic)

Before
```go
}
}
```
After
```go
}
}

// Advanced form of the above forged blockchain attack, where not only does the
// attacker make up a valid hashes for random blocks, but also forges the block
// parents to point to existing hashes.
func TestMadeupParentBlockChainAttack(t *testing.T) {
	defaultBlockTTL := blockTTL
```

# Fix Pattern

Record the exact relationship to be verified later, then compare against that recorded value instead of using a broader local-state predicate.

## How It Was Fixed

The fix introduced a `crossCheck` record containing both expiry and expected parent hash. The downloader now uses that record when the sampled block arrives and returns `ErrCrossCheckFailed` if the block's parent does not match the stored parent. The existing timeout behavior was preserved through `check.expire`, and a regression test was added for the forged-parent scenario.

# Why It Matters

1. The downloader now enforces exact parent binding for sampled blocks.

2. A malicious peer can no longer satisfy the cross-check by pointing to an arbitrary queued parent.

3. The evidence shows a verification-bypass fix in sync logic, not a generic resource-control change.

4. The diff does not establish impact beyond downloader acceptance or rejection behavior.

# Evidence Notes

The strongest support is the direct replacement of `!d.queue.Has(block.ParentHash())` with `block.ParentHash() != check.parent`, together with the new `crossCheck { expire, parent }` state and the added forged-parent regression test. Claims about broader consensus impact, full-chain acceptance, or resource exhaustion are not established by the provided snippets. Protocol security invariant: A downloader cross-check for a sampled block hash must validate the returned block against the specific recorded parent for that sample. Checking only that the block references some parent already present in local queued state is too weak. Verification notes: The patch proves a downloader cross-check bypass, not that forged chains would necessarily pass all later consensus or block-validation stages. The evidence does not show remote code execution, memory corruption, or privilege escalation. The patch does not by itself prove broad resource exhaustion; the primary change is ancestry-integrity verification. The exact exploit impact beyond sync-path acceptance or delayed rejection is not established by the diff alone. The narrow downloader-integrity claim is directly supported by the changed condition. The evidence does not show the full lifecycle where `check.parent` is populated, but the new field and equality check make the intended invariant clear. The patch should not be described as a proven consensus-bypass or DoS fix based on this evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `verification-bypass`
Final impact type: `sync-integrity-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, downloader, peer-input, integrity-check`

The patch is security-relevant and supports keeping this case in a security corpus, but not under the original resource-exhaustion/remote-dos framing. The code changes a network-facing downloader cross-check from a weak predicate that accepted any queued parent to an exact parent comparison recorded earlier, and the added test explicitly models a forged-parent attack from a malicious peer. That is strong evidence of a real verification-bypass fix in security-sensitive sync logic, even though the provided patch does not prove broader consensus compromise or denial-of-service impact.

## Security Evidence

1. The fix replaces `!d.queue.Has(block.ParentHash())` with `block.ParentHash() != check.parent`, tightening validation from local membership to exact expected ancestry.
2. A new `crossCheck` structure stores the expected parent hash, showing the prior state was insufficient for later verification.
3. The added regression test is explicitly described as an "advanced" forged blockchain attack using forged parents that point to existing hashes.
4. The failure mode is `ErrCrossCheckFailed`, indicating the patch is meant to reject attacker-controlled invalid chain data during synchronization.

## Missing Evidence

1. The patch does not show whether the forged chain would survive later consensus or full block validation stages.
2. The evidence does not demonstrate measurable resource exhaustion or a reliable remote denial-of-service condition.
3. The provided snippets do not show the full lifecycle of how `check.parent` is populated, only that it is later enforced.

## Claim Boundaries

1. Supported claim: a malicious peer could bypass this downloader cross-check by using a known queued parent instead of the correct parent.
2. Supported claim: the fix strengthens sync-path integrity verification for sampled blocks.
3. Not supported: proven consensus bypass, chain takeover, or acceptance of an invalid chain by the full system.
4. Not supported: classifying this as resource-exhaustion or remote-dos from the provided patch alone.
