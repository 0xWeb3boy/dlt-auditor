---
case_id: case_20150521_52db6d8be5
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
date: 2015-05-21
source_refs:
  - git:52db6d8be577669bd5ba659ac223acf61956b05a
  - "eth/downloader/downloader.go:333"
  - "eth/downloader/downloader.go:324"
  - "eth/downloader/downloader.go:62"
  - "eth/downloader/downloader_test.go:526"
bug_class: validation-bypass
impact_type:
  - sync-integrity
tags:
  - blockchain-core
  - downloader
  - block-sync
  - validation-bypass
  - forged-chain
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a downloader cross-check weakness in go-ethereum. Previously, a checked block passed validation if its parent hash was merely present in the local queue. The fix records the expected parent for each pending cross-check and rejects the block unless `block.ParentHash()` equals that stored parent. The added test explicitly covers a forged blockchain attack where forged blocks point to existing parent hashes.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `for hash, deadline := range d.checks {` with `for hash, check := range d.checks {`.

2. In `eth/downloader/downloader.go`, the patch replaces `if _, ok := d.checks[block.Hash()]; ok {` with `if check, ok := d.checks[block.Hash()]; ok {`.

3. In `eth/downloader/downloader.go`, the patch replaces `mux *event.TypeMux` with `type crossCheck struct {`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Advanced form of the above forged blockchain attack, where not only does the`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `checks`, `block`, `hash`, and `check`.

## Before/After Behavior

Before the patch, `d.checks` stored only an expiry deadline, and the downloader accepted a checked block when `d.queue.Has(block.ParentHash())` was true. After the patch, `d.checks` stores a `crossCheck` containing both expiry and expected parent, and validation fails when the returned block's parent differs from `check.parent`. Timeout handling now reads `check.expire`.

# Root Cause

The cross-check predicate was too weak: it verified parent membership in the queue rather than the exact parent-child relationship expected for the checked hash.

## Walkthrough

1. The downloader maintained pending cross-checks in `d.checks`, keyed by block hash.

2. The old map value stored only a timeout deadline.

3. When a one-block response matched a pending cross-check hash, the old code checked whether the block's parent hash existed in the downloader queue.

4. That allowed a forged block to pass this check if it referenced any queued parent hash, even when it was not the expected parent for the checked hash.

5. The patch introduces `crossCheck` state containing `expire` and `parent`.

6. The verification path now compares `block.ParentHash()` directly with `check.parent` and returns `ErrCrossCheckFailed` on mismatch.

7. The timeout loop was updated to use `check.expire` after the map value type changed.

8. The new regression test covers forged blocks whose parents point to existing hashes and expects synchronization to fail.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 62 | adds `crossCheck` state carrying expiry and expected parent hash for pending hash-chain cross checks |
| eth/downloader/downloader.go | 324 | validates downloaded cross-check blocks against the expected parent hash instead of only queue membership |
| eth/downloader/downloader.go | 333 | updates timeout handling to use the new cross-check expiry field |
| eth/downloader/downloader_test.go | 526 | adds regression coverage for forged blocks whose parents point to existing hashes |

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

Bind deferred validation state to the exact relationship that must later be verified, rather than using a broader membership check as a proxy.

## How It Was Fixed

The fix changes pending cross-check state from `map[common.Hash]time.Time` to `map[common.Hash]*crossCheck`, adds storage for the expected parent hash, checks returned blocks against that exact parent, preserves expiry behavior through `check.expire`, and adds regression coverage for the known-parent forged-chain case.

# Why It Matters

1. Prevents a forged downloader cross-check from passing through a weaker parent-in-queue condition.

2. Preserves the expected parent-child relation during block synchronization checks.

3. The evidence supports a downloader validation bypass, not remote code execution, memory corruption, cryptographic primitive failure, or full consensus-rule bypass.

4. The regression test documents the specific known-parent forged-chain scenario.

# Evidence Notes

Evidence comes from `eth/downloader/downloader.go`, where `crossCheck` adds `expire` and `parent`, validation changes from `!d.queue.Has(block.ParentHash())` to `block.ParentHash() != check.parent`, and timeout handling changes from a deadline map value to `check.expire`. Evidence also comes from `eth/downloader/downloader_test.go`, where `TestMadeupParentBlockChainAttack` describes forged block parents pointing to existing hashes. The claim is limited to downloader cross-check validation. Protocol security invariant: During block synchronization, a block returned for a pending cross-check must have the exact expected parent hash for that checked hash. It is not sufficient for the parent hash to be present somewhere in the downloader queue. Verification notes: Does not prove remote code execution or memory corruption. Does not prove a consensus-rule bypass after full block validation. Does not quantify resource exhaustion impact. Does not show a cryptographic primitive weakness; the issue is downloader chain-relation validation. Does not prove all malicious peers can force canonical-chain acceptance, only that this forged sync path previously passed the weaker cross-check condition. Commit subject explicitly identifies a forged blockchain with known-parent attack. Implementation change directly strengthens the checked parent condition. Regression test covers the forged-parent case. No evidence supports broader claims such as resource exhaustion, RCE, memory corruption, cryptographic weakness, or final consensus acceptance. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `validation-bypass`
Final impact type: `sync-integrity`
Final tags: `blockchain-core, downloader, block-sync, validation-bypass, forged-chain`

The supplied patch evidence supports a security fix: the downloader previously accepted a cross-check block if its parent hash was merely present in the queue, and the fix binds each pending check to the exact expected parent hash. The commit subject and added regression test explicitly describe a forged blockchain attack using known parent hashes. However, the original resource-exhaustion and remote-DoS classification is too specific for the evidence; the supported issue is a downloader validation bypass affecting block-sync integrity.

## Security Evidence

1. Commit subject explicitly references a forged blockchain with known-parent attack.
2. Validation changed from broad queue membership, `d.queue.Has(block.ParentHash())`, to exact parent comparison, `block.ParentHash() != check.parent`.
3. New `crossCheck` state stores both expiry and expected parent hash for pending checks.
4. Regression test describes attackers forging block parents to point to existing hashes and expects sync failure.

## Missing Evidence

1. No evidence quantifies resource exhaustion or remote DoS impact.
2. No evidence proves final canonical-chain acceptance or consensus-rule bypass.
3. No evidence supports RCE, memory corruption, or cryptographic primitive failure.

## Claim Boundaries

1. Keep claim limited to downloader cross-check validation bypass.
2. Impact should be framed as block synchronization integrity, not proven chain consensus compromise.
3. The evidence supports malicious peer or forged-chain handling, but not broader node takeover or availability impact.
