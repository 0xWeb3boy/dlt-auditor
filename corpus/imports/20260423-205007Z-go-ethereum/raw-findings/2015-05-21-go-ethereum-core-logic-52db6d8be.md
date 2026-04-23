---
case_id: case_20150521_52db6d8be
project: go-ethereum
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
bug_class: cross-check-validation-bypass
impact_type:
  - sync-integrity
confidence: high
tags:
  - blockchain-core
  - downloader
  - peer-sync
  - validation-bypass
  - forged-chain
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a downloader validation weakness where forged blocks could satisfy cross-checks by pointing their parent hash at any known queued hash. The fix records the expected parent hash with each pending cross-check and requires the returned block to match it exactly.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `for hash, deadline := range d.checks {` with `for hash, check := range d.checks {`.

2. In `eth/downloader/downloader.go`, the patch replaces `if _, ok := d.checks[block.Hash()]; ok {` with `if check, ok := d.checks[block.Hash()]; ok {`.

3. In `eth/downloader/downloader.go`, the patch replaces `mux *event.TypeMux` with `type crossCheck struct {`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Advanced form of the above forged blockchain attack, where not only does the`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `checks`, `block`, `hash`, and `check`.

## Before/After Behavior

Before the patch, d.checks stored only an expiry deadline. When a checked block arrived, the downloader accepted it if block.ParentHash() existed in the queue. After the patch, d.checks stores both expiry and expected parent, and the downloader rejects the block unless block.ParentHash() equals the recorded parent. Timeout handling is preserved through the new expire field.

# Root Cause

The downloader used queue membership as a proxy for validating the parent-child relationship of a cross-checked block. Because the expected parent was not retained in the cross-check state, a malicious peer could craft parent links to known hashes and pass the weaker check.

## Walkthrough

1. Pending cross-checks were previously keyed by block hash and stored only a deadline.

2. A returned block whose hash was pending was validated by checking whether its parent hash was present in the queue.

3. That check did not prove the block belonged to the expected hash-chain position.

4. The patch introduces a crossCheck structure containing both expire and parent.

5. The validation path now compares block.ParentHash() directly with check.parent.

6. If the parent does not match, synchronization fails with ErrCrossCheckFailed.

7. The added regression test documents the forged-parent blockchain attack case.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 62 | stores pending cross-check metadata including expiry and expected parent hash |
| eth/downloader/downloader.go | 324 | validates returned cross-check block against the exact expected parent |
| eth/downloader/downloader.go | 333 | preserves timeout handling using the new cross-check expiry field |
| eth/downloader/downloader_test.go | 526 | regression test for forged parent blockchain attack |

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

Store the exact validation predicate needed for later checks, then compare peer-supplied data against that expected value instead of using approximate membership tests.

## How It Was Fixed

The patch changes d.checks from a map of hash to deadline into a map of hash to crossCheck metadata, adds an expected parent hash to that metadata, updates timeout handling to use check.expire, and replaces d.queue.Has(block.ParentHash()) with block.ParentHash() == check.parent.

# Why It Matters

1. Prevents malicious peers from passing downloader cross-checks with forged parent links.

2. Preserves the expected hash-chain relationship during synchronization.

3. Fails suspicious synchronization locally with ErrCrossCheckFailed.

4. Does not prove arbitrary code execution, key compromise, or fund theft.

# Evidence Notes

The evidence directly supports a security fix in eth/downloader: the commit subject names a forged blockchain attack, the implementation changes parent validation semantics, and the added test describes forged parents pointing to existing hashes. The evidence does not establish that invalid consensus blocks could be imported after full validation or quantify broader network impact. Protocol security invariant: During downloader synchronization, a peer-supplied block selected for cross-check must have the exact expected parent from the advertised hash chain; it is not enough for the parent hash to merely exist somewhere in the local download queue. Verification notes: Does not prove consensus invalid blocks could be imported after full validation. Does not prove arbitrary code execution, key compromise, or fund theft. Does not quantify resource exhaustion impact. Does not show a complete network exploit trace beyond a malicious peer influencing downloader synchronization. Regression coverage is shown by TestMadeupParentBlockChainAttack. No command output or test execution results were provided. Claims are limited to downloader synchronization cross-check bypass behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `cross-check-validation-bypass`
Final impact type: `sync-integrity`
Final confidence: `high`
Final tags: `blockchain-core, downloader, peer-sync, validation-bypass, forged-chain`

The supplied evidence strongly supports a security fix: the commit subject and added regression test explicitly describe a forged blockchain attack, and the implementation replaces a weak queue-membership parent check with an exact expected-parent comparison for downloader cross-checks. The original resource-exhaustion and remote-DoS framing is too specific for the provided patch evidence; the safer validated claim is a downloader synchronization validation bypass involving forged parent hashes.

## Security Evidence

1. Commit subject names a forged blockchain with known parent attack.
2. Regression test describes an attacker forging block parents to point to existing hashes.
3. Patch changes cross-check state to retain the expected parent hash, not just an expiry deadline.
4. Patch rejects a returned cross-check block when block.ParentHash() does not equal the recorded expected parent.
5. The affected code is in peer-driven blockchain downloader synchronization logic.

## Missing Evidence

1. No evidence shows invalid consensus blocks could be imported after full validation.
2. No exploit trace or network-wide impact is provided.
3. No evidence quantifies resource exhaustion or proves remote denial of service.
4. No test execution output is supplied.

## Claim Boundaries

1. Keep the finding limited to downloader cross-check validation bypass by malicious or faulty peers.
2. Do not claim arbitrary code execution, key compromise, fund theft, or consensus validation bypass.
3. Do not retain resource-exhaustion or remote-DoS as the primary impact without additional evidence.
4. The patch proves stricter synchronization validation, not broader consensus-layer compromise.
