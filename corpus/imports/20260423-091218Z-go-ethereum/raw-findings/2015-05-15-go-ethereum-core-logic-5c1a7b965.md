---
case_id: case_20150515_5c1a7b965
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
bug_class: p2p-sync-validation-bypass
impact_type:
  - p2p-sync-disruption
tags:
  - blockchain-core
  - p2p
  - downloader
  - sync-validation
  - fake-chain
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a downloader validation flaw for a fake blockchain attack. Previously, a pending random cross-check could be cleared when the peer returned a block with the expected hash, without checking whether that block linked back to the queued chain segment. The fix rejects such disconnected sampled blocks with ErrCrossCheckFailed.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `hash := blockPack.blocks[0].Hash()` with `block := blockPack.blocks[0]`.

2. In `eth/downloader/downloader_test.go`, the patch replaces `for i, hash := range hashes {` with `for i := 0; i < len(hashes); i++ {`.

3. In `eth/downloader/downloader_test.go`, the patch replaces `copy(reverse, hashes)` with `chunk1 := make([]common.Hash, blockCacheLimit)`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Tests that if a malicious peer makes up a random block chain, and tried to`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `hashes`, `Hash`, `blocks`, and `blockCacheLimit`.

## Before/After Behavior

Before the patch, fetchHashes handled a one-block cross-check response by computing the returned block hash and deleting d.checks[hash]. The provided code shows no parent-link validation before clearing the check. After the patch, fetchHashes only acts when block.Hash() is pending in d.checks, verifies d.queue.Has(block.ParentHash()), returns ErrCrossCheckFailed if the parent is not queued, and deletes the pending check only after that validation succeeds. The tests were updated to create linked block fixtures and add coverage for fabricated block-chain material.

# Root Cause

The cross-check path treated a returned block hash match as sufficient and cleared the pending check without confirming that the returned block's parent belonged to the downloader's queued hash chain.

## Walkthrough

1. A malicious peer can participate in eth/downloader hash synchronization.

2. The downloader maintains pending random block checks in d.checks while hash-derived work is tracked in the queue.

3. Before the fix, a one-block response from the active peer caused the matching d.checks entry to be deleted based only on block.Hash().

4. The pre-fix code did not inspect block.ParentHash() before clearing the pending check.

5. That allowed a fabricated or disconnected block chain to satisfy the sampled-hash check without proving linkage to the advertised queued chain segment.

6. After the fix, fetchHashes first confirms the returned block hash is pending in d.checks.

7. For pending checks, it then requires the returned block's parent hash to exist in d.queue.

8. If the parent hash is missing, synchronization fails with ErrCrossCheckFailed.

9. Only a sampled block whose parent is present in the queue clears the pending check.

10. The tests support this by generating parent-linked fixtures and adding or adjusting attack-oriented regression cases.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 303 | Validates random block cross-check responses during hash fetching and rejects disconnected parent links. |
| eth/downloader/downloader_test.go | 37 | Builds test block fixtures with parent links matching the supplied hash sequence. |
| eth/downloader/downloader_test.go | 426 | Regression coverage for invalid hash ordering attacks against downloader chain validation. |
| eth/downloader/downloader_test.go | 457 | Regression coverage for made-up hash chains failing with ErrCrossCheckFailed. |
| eth/downloader/downloader_test.go | 469 | Regression coverage for made-up block chains being caught during cross-checking. |

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

Strengthen protocol cross-check validation by requiring structural parent linkage before accepting and clearing a sampled block check.

## How It Was Fixed

The implementation changed from unconditional deletion of d.checks[hash] to conditional validation: if block.Hash() is pending, fetchHashes verifies d.queue.Has(block.ParentHash()), returns ErrCrossCheckFailed on a missing parent, and deletes the check only after the parent-link check succeeds. Test helper code was adjusted to build linked block sequences, and regression coverage was added for made-up block-chain behavior.

# Why It Matters

1. Prevents malicious peers from passing downloader cross-checks with disconnected fake chain material.

2. Preserves the invariant that sampled blocks must link to the queued hash chain.

3. Keeps the impact scoped to downloader synchronization validation.

4. Does not establish remote code execution, key compromise, or consensus-rule bypass.

# Evidence Notes

The strongest evidence is eth/downloader/downloader.go:303, where parent-hash queue membership is newly required before deleting a pending cross-check entry. Supporting evidence comes from eth/downloader/downloader_test.go, where fixtures now encode parent links and tests cover invalid ordering, made-up hash chains, and made-up block chains. The commit subject explicitly references a fake blockchain attack. Claims about CPU, memory, bandwidth exhaustion, cryptographic breakage, or broader consensus compromise are not established by the provided evidence. Protocol security invariant: During downloader hash-chain synchronization, a block returned for a pending random cross-check must be linked to the queued hash chain: matching the sampled block hash is not enough if the block's parent hash is absent from the downloader queue. Verification notes: The patch does not prove remote code execution or memory corruption. The patch does not prove private key, account, or fund compromise. The patch does not prove a consensus-rule bypass outside the downloader synchronization path. The patch does not quantify CPU, memory, or bandwidth exhaustion impact. The evidence only supports malicious peer fake-chain/cross-check validation failure in eth/downloader. Implementation evidence directly shows the missing parent-link check being added. Regression tests are security-relevant support code, not the root cause. No evidence provided for resource-exhaustion impact beyond failed downloader validation. No evidence provided for effects outside eth/downloader synchronization. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `p2p-sync-validation-bypass`
Final impact type: `p2p-sync-disruption`
Final tags: `blockchain-core, p2p, downloader, sync-validation, fake-chain`

The supplied evidence supports keeping this as a security fix. The implementation changes downloader cross-check handling from clearing a pending check based only on a returned block hash to requiring that the returned block's parent hash is present in the queued chain, failing with ErrCrossCheckFailed otherwise. The commit subject and added tests explicitly frame this as catching malicious fake blockchain behavior. However, the original resource-exhaustion and remote-DoS framing is somewhat stronger than the patch alone proves, so the corpus entry should be scoped to P2P sync validation against fake-chain material.

## Security Evidence

1. Commit subject explicitly says it circumvents a fake blockchain attack.
2. Downloader code now rejects a sampled block whose parent is not in the queued chain.
3. The old code deleted the pending cross-check entry using only the returned block hash.
4. Tests add malicious-peer fake blockchain coverage expecting ErrCrossCheckFailed.
5. Test helpers were changed to model parent-linked block sequences, supporting the parent-link validation invariant.

## Missing Evidence

1. No quantified CPU, memory, or bandwidth exhaustion impact is shown.
2. No evidence of code execution, key compromise, or fund theft is shown.
3. No evidence proves consensus-rule bypass outside downloader synchronization.
4. No broader network-wide DoS impact is established from the supplied patch alone.

## Claim Boundaries

1. This supports a security fix in the eth/downloader P2P synchronization path.
2. The validated issue is fake-chain or disconnected-chain acceptance during cross-checking.
3. Impact should be described as sync disruption or malicious peer validation bypass, not a proven general remote DoS.
4. Regression tests are supporting evidence, while the core fix is the parent-hash queue membership check.
