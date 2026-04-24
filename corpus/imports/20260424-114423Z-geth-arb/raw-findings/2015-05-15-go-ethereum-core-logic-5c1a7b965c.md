---
case_id: case_20150515_5c1a7b965c
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
  - git:5c1a7b965ca7901d3b185d75205419b87163a4fa
  - "eth/downloader/downloader.go:303"
  - "eth/downloader/downloader_test.go:37"
  - "eth/downloader/downloader_test.go:429"
  - "eth/downloader/downloader_test.go:469"
bug_class: protocol-validation-bypass
impact_type:
  - malicious-peer-sync-disruption
tags:
  - blockchain-core
  - p2p-sync
  - downloader
  - protocol-validation
  - malicious-peer
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a malicious-peer downloader validation bypass. Before the change, fetchHashes cleared a pending cross-check based only on the returned block hash. After the change, it only clears the check if the returned block hash is pending and the block's parent hash is present in the downloader queue; otherwise it returns ErrCrossCheckFailed.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `hash := blockPack.blocks[0].Hash()` with `block := blockPack.blocks[0]`.

2. In `eth/downloader/downloader_test.go`, the patch replaces `for i, hash := range hashes {` with `for i := 0; i < len(hashes); i++ {`.

3. In `eth/downloader/downloader_test.go`, the patch replaces `copy(reverse, hashes)` with `chunk1 := make([]common.Hash, blockCacheLimit)`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Tests that if a malicious peer makes up a random block chain, and tried to`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `hashes`, `Hash`, `blocks`, and `blockCacheLimit`.

## Before/After Behavior

Before the patch, a single-block cross-check response from the active peer caused fetchHashes to compute the returned block hash and delete that hash from d.checks, without checking whether the block connected to the queued parent chain. After the patch, the code first confirms the block hash is in d.checks, then verifies d.queue.Has(block.ParentHash()), and fails with ErrCrossCheckFailed if the parent is not queued. Tests were updated so generated blocks form parent-linked chains, invalid-order coverage was adjusted for that model, and a made-up blockchain attack regression test was added.

# Root Cause

The downloader's cross-check completion logic relied on the returned block hash alone. It lacked a parent-hash membership check against the downloader queue before accepting the cross-check result, allowing a disconnected or fabricated block response to clear pending cross-check state.

## Walkthrough

1. fetchHashes receives block packs from the active peer and only considers packs containing exactly one block.

2. Before the fix, the code deleted the returned block hash from d.checks without validating the block's parent relationship to the queued chain.

3. The patch stores the returned block, checks whether block.Hash() is actually pending in d.checks, and applies validation only for pending checks.

4. For pending checks, the patch requires d.queue.Has(block.ParentHash()).

5. If the parent hash is not in the queue, fetchHashes returns ErrCrossCheckFailed instead of clearing the check.

6. The test helper now creates parent-linked synthetic blocks rather than blocks all sharing knownHash as parent.

7. The invalid hash-order test was adjusted to reorder chunks under the parent-linked model.

8. A new TestMadeupBlockChainAttack verifies that a malicious peer supplying a fabricated chain is rejected with ErrCrossCheckFailed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 303 | Adds parent-hash queue membership validation before accepting a cross-check block and deleting its pending check. |
| eth/downloader/downloader_test.go | 37 | Updates test block construction so generated blocks form a parent-linked chain matching the hash order. |
| eth/downloader/downloader_test.go | 429 | Adjusts invalid hash order attack test to exercise reordered chunks under the parent-link model. |
| eth/downloader/downloader_test.go | 469 | Adds regression coverage for a malicious peer supplying a made-up block chain that should be caught by cross-check failure. |

## Code Snippets

## Snippet 1

Context: `eth/downloader/downloader.go:303` (changes signature or replay validation logic)

Before
```go
continue
			}
			hash := blockPack.blocks[0].Hash()
			delete(d.checks, hash)

		case <-crossTicker.C:
```
After
```go
continue
			}
			block := blockPack.blocks[0]
			if _, ok := d.checks[block.Hash()]; ok {
				if !d.queue.Has(block.ParentHash()) {
					return ErrCrossCheckFailed
				}
				delete(d.checks, block.Hash())
```

## Snippet 2

Context: `eth/downloader/downloader_test.go:37` (changes signature or replay validation logic)

Before
```go
func createBlocksFromHashes(hashes []common.Hash) map[common.Hash]*types.Block {
	blocks := make(map[common.Hash]*types.Block)

	for i, hash := range hashes {
		blocks[hash] = createBlock(len(hashes)-i, knownHash, hash)
	}

	return blocks
```
After
```go
func createBlocksFromHashes(hashes []common.Hash) map[common.Hash]*types.Block {
	blocks := make(map[common.Hash]*types.Block)
	for i := 0; i < len(hashes); i++ {
		parent := knownHash
		if i < len(hashes)-1 {
			parent = hashes[i+1]
		}
		blocks[hashes[i]] = createBlock(len(hashes)-i, parent, hashes[i])
```

## Snippet 3

Context: `eth/downloader/downloader_test.go:429` (changes signature or replay validation logic)

Before
```go
blocks := createBlocksFromHashes(hashes)

	reverse := make([]common.Hash, len(hashes))
	copy(reverse, hashes)

	for i := len(hashes) / 4; i < 2*len(hashes)/4; i++ {
		reverse[i], reverse[len(hashes)-i-1] = reverse[len(hashes)-i-1], reverse[i]
	}
```
After
```go
blocks := createBlocksFromHashes(hashes)

	chunk1 := make([]common.Hash, blockCacheLimit)
	chunk2 := make([]common.Hash, blockCacheLimit)
	copy(chunk1, hashes[blockCacheLimit:2*blockCacheLimit])
	copy(chunk2, hashes[2*blockCacheLimit:3*blockCacheLimit])

	reverse := make([]common.Hash, len(hashes))
```

## Snippet 4

Context: `eth/downloader/downloader_test.go:469` (changes signature or replay validation logic)

Before
```go
}
}
```
After
```go
}
}

// Tests that if a malicious peer makes up a random block chain, and tried to
// push indefinitely, it actually gets caught with it.
func TestMadeupBlockChainAttack(t *testing.T) {
	blockTTL = 100 * time.Millisecond
	crossCheckCycle = 25 * time.Millisecond
```

# Fix Pattern

Validate structural chain membership before clearing protocol cross-check state.

## How It Was Fixed

In eth/downloader/downloader.go, the cross-check path now gates deletion from d.checks on both a pending-check lookup and a parent-hash queue membership check. In eth/downloader/downloader_test.go, supporting tests were updated to construct realistic parent-linked chains and to cover made-up chain rejection.

# Why It Matters

1. Prevents a malicious peer from satisfying downloader cross-checks with disconnected or fabricated blocks.

2. Preserves the expected relationship between advertised hashes, returned blocks, and the queued parent chain.

3. Supports a protocol validation bypass finding without claiming memory corruption, remote code execution, hash compromise, or canonical-chain acceptance.

# Evidence Notes

The strongest evidence is the implementation change at eth/downloader/downloader.go:303, where delete(d.checks, block.Hash()) is moved behind a pending-check lookup and d.queue.Has(block.ParentHash()) validation, with ErrCrossCheckFailed on failure. Supporting evidence is in eth/downloader/downloader_test.go: createBlocksFromHashes now builds parent-linked blocks, TestInvalidHashOrderAttack is adapted, and TestMadeupBlockChainAttack is added. The evidence supports malicious-peer sync validation bypass, not resource-exhaustion as the primary class and not a cryptographic break. Protocol security invariant: During downloader peer sync, a cross-checked block must not satisfy validation by hash alone; if the block hash is pending in the cross-check set, its parent hash must also be present in the downloader queue, otherwise the peer data is treated as an invalid or disconnected chain and sync fails with ErrCrossCheckFailed. Verification notes: The patch does not prove remote code execution or memory corruption. The patch does not show that consensus-invalid blocks could be permanently accepted into the canonical chain. The patch does not quantify CPU, memory, or bandwidth impact from the attack. The patch evidence supports malicious-peer sync validation failure, not a cryptographic hash break. Commit subject explicitly describes circumventing a fake blockchain attack. Regression coverage expects ErrCrossCheckFailed for made-up hash and block chain attack scenarios. No provided evidence establishes remote code execution, memory corruption, quantified resource exhaustion, or permanent acceptance of consensus-invalid blocks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `protocol-validation-bypass`
Final impact type: `malicious-peer-sync-disruption`
Final tags: `blockchain-core, p2p-sync, downloader, protocol-validation, malicious-peer`

The evidence supports keeping this as a security fix, but the original resource-exhaustion and remote-DoS framing is stronger than the patch proves. The commit explicitly describes a fake blockchain attack, the code adds parent-hash queue membership validation before clearing cross-check state, and regression tests model malicious peers with made-up hash/block chains expecting ErrCrossCheckFailed. A conservative corpus entry should frame this as a malicious-peer downloader validation bypass rather than a quantified resource exhaustion issue.

## Security Evidence

1. Commit subject explicitly says it circumvents a fake blockchain attack.
2. Downloader cross-check logic now verifies the returned block hash is pending before accepting it.
3. For pending checks, the patch requires block.ParentHash() to exist in the downloader queue.
4. Invalid parent linkage now returns ErrCrossCheckFailed instead of clearing d.checks.
5. Tests add malicious made-up block chain coverage expecting synchronization to fail with ErrCrossCheckFailed.

## Missing Evidence

1. No evidence quantifies CPU, memory, bandwidth, or persistent resource exhaustion impact.
2. No evidence shows permanent acceptance of consensus-invalid blocks into the canonical chain.
3. No evidence supports cryptographic hash compromise, memory corruption, or code execution.
4. No network-level exploit trace or adversary capability details are provided beyond malicious peer behavior.

## Claim Boundaries

1. Valid claim: malicious peer data could bypass downloader cross-check validation by hash alone.
2. Valid claim: the fix enforces parent linkage against queued downloader state before accepting a cross-check block.
3. Do not claim a cryptographic vulnerability or hash collision issue.
4. Do not claim proven remote DoS as the primary impact from this patch alone.
5. Do not claim consensus safety failure or canonical chain corruption without additional evidence.
