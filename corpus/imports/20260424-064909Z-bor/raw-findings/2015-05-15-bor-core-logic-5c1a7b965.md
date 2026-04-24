---
case_id: case_20150515_5c1a7b965
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: high
date: 2015-05-15
source_refs:
  - git:5c1a7b965ca7901d3b185d75205419b87163a4fa
  - "eth/downloader/downloader.go:303"
  - "eth/downloader/downloader_test.go:37"
  - "eth/downloader/downloader_test.go:429"
  - "eth/downloader/downloader_test.go:469"
bug_class: insufficient-peer-chain-validation
impact_type:
  - sync-integrity-risk
confidence: medium
tags:
  - blockchain-core
  - downloader
  - peer-validation
  - chain-continuity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a downloader validation flaw in which a peer could satisfy a cross-check with a block hash alone, without proving parent continuity to the queued chain. The patch tightens that check and the tests were updated to exercise reordered or made-up chain data. The security relevance is plausible and supported by the live-code change, but the provided excerpts do not prove downstream consensus impact, so confidence should be kept below high.

## Observed Patch Facts

1. In `eth/downloader/downloader.go`, the patch replaces `hash := blockPack.blocks[0].Hash()` with `block := blockPack.blocks[0]`.

2. In `eth/downloader/downloader_test.go`, the patch replaces `for i, hash := range hashes {` with `for i := 0; i < len(hashes); i++ {`.

3. In `eth/downloader/downloader_test.go`, the patch replaces `copy(reverse, hashes)` with `chunk1 := make([]common.Hash, blockCacheLimit)`.

4. In `eth/downloader/downloader_test.go`, the patch adds `// Tests that if a malicious peer makes up a random block chain, and tried to`.

## Project Context

The changed code sits primarily in `eth/downloader`, which anchors the finding in the `core-logic` area of the project. Historical context from `eth/downloader/queue.go`, `eth/downloader/queue_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/queue.go`, `eth/downloader/queue_test.go`. The strongest project-level identifiers around this patch are `hashes`, `Hash`, `blocks`, and `blockCacheLimit`.

## Before/After Behavior

Before the patch, the block-receipt path in `fetchHashes` took `blockPack.blocks[0].Hash()` and unconditionally deleted the matching entry from `d.checks`. After the patch, it uses the full block object, and if the block is being cross-checked it requires `d.queue.Has(block.ParentHash())`; otherwise it returns `ErrCrossCheckFailed` instead of clearing the check. The tests were updated so generated blocks have parent linkage, and attack-oriented tests were adjusted or added to cover reordered and fabricated chains.

# Root Cause

Cross-check state was advanced based only on receipt of a block with the expected hash, without verifying that the block's parent matched the queued chain state.

## Walkthrough

1. In `eth/downloader/downloader.go`, the old logic deleted a pending cross-check entry as soon as a single block with the tracked hash arrived from the active peer.

2. The patch changes that path to inspect the full block, not just its hash.

3. If the block hash is one of the tracked checks, the new code verifies that the block's parent is already present in `d.queue`.

4. When that parent is missing, the downloader now returns `ErrCrossCheckFailed` instead of accepting the block for cross-check purposes.

5. In `eth/downloader/downloader_test.go`, `createBlocksFromHashes` was changed so test blocks point to the next hash as parent rather than all sharing `knownHash`.

6. `TestInvalidHashOrderAttack` was reworked to move chunk-sized regions of hashes, making parent-order problems observable under the new check.

7. A new `TestMadeupBlockChainAttack` was added, which is consistent with the fix targeting fabricated chain progression from a malicious peer.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/downloader/downloader.go | 303 | core hash/block sync path in `fetchHashes`; cross-check acceptance now requires queued parent continuity before clearing verification state |
| eth/downloader/downloader_test.go | 37 | test helper updated to construct blocks with correct parent linkage so chain-continuity checks are meaningful |
| eth/downloader/downloader_test.go | 429 | attack regression test for invalid hash ordering across cached chunks |
| eth/downloader/downloader_test.go | 469 | attack regression test for fabricated block chains that should now trigger `ErrCrossCheckFailed` |

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

Require structural consistency before advancing verification state, and add adversarial tests that model the required parent-child relationships.

## How It Was Fixed

The fix gates removal of entries from `d.checks` on a parent-continuity check against the downloader queue and fails fast with `ErrCrossCheckFailed` when that continuity is absent. Supporting tests were strengthened by building parent-linked block fixtures and adding scenarios for reordered or fabricated chains.

# Why It Matters

1. A peer can no longer satisfy this cross-check with a matching block hash alone.

2. Disconnected or fabricated chain segments are more likely to be rejected before they advance downloader state.

3. The updated tests make ancestry-sensitive validation explicit and regression-testable.

# Evidence Notes

The strongest production evidence is the `fetchHashes` hunk in `eth/downloader/downloader.go`, where unconditional `delete(d.checks, hash)` was replaced with a `d.queue.Has(block.ParentHash())` guard and `ErrCrossCheckFailed` on failure. Test support comes from `eth/downloader/downloader_test.go`: block fixtures were changed to encode parent linkage, `TestInvalidHashOrderAttack` was reshaped around chunk reordering, and a new `TestMadeupBlockChainAttack` was added. The excerpts support a malformed/fabricated chain validation issue in the downloader, but they do not establish full consensus compromise or quantify denial-of-service impact. Protocol security invariant: The downloader should clear a pending cross-check only for a block that both matches the expected hash and connects to the queued chain through its parent; a matching hash by itself is not sufficient. Verification notes: The patch does not prove consensus compromise or chain acceptance beyond the downloader stage. The patch does not show remote code execution, memory corruption, or cryptographic breakage. The exact resource-exhaustion impact is not quantified by the diff. The evidence shows malformed or fabricated chain progression being rejected, not a general exploit against all sync modes. The live-code evidence is limited to a single acceptance-path hunk in `fetchHashes`. The test changes materially support the interpretation that parent continuity, not just hash matching, is the intended invariant. The provided excerpts do not prove what happens beyond the downloader stage. The exact exploit impact remains unquantified in the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-peer-chain-validation`
Final impact type: `sync-integrity-risk`
Final confidence: `medium`
Final tags: `blockchain-core, downloader, peer-validation, chain-continuity`

The patch clearly tightens a security-sensitive validation path in the downloader: a peer-supplied block no longer clears a cross-check based on hash alone, but must also connect to the queued chain through its parent. The added tests explicitly model malicious fabricated or reordered chain data, so the change is plausibly security-motivated and corpus-worthy. However, the supplied diff does not prove a concrete exploitable outcome such as consensus compromise or a quantified remote DoS, so this is better treated as security hardening than as a fully proven security fix for resource exhaustion.

## Security Evidence

1. Live code adds a parent-continuity check before deleting an entry from `d.checks`.
2. Failure path now returns `ErrCrossCheckFailed` when a checked block's parent is missing from the queue.
3. Commit subject explicitly references a `fake blockchain attack`.
4. Tests were updated to give blocks real parent linkage, making ancestry validation meaningful.
5. New and updated tests explicitly describe malicious peers, invalid hash order, and made-up block chains.

## Missing Evidence

1. No production-path evidence shows what concrete impact the old behavior enabled beyond downloader acceptance logic.
2. The diff does not demonstrate consensus compromise, chain acceptance, or permanent state corruption.
3. The patch does not quantify resource exhaustion or prove a reliable remote denial-of-service outcome.
4. Only a narrow validation hunk is shown; surrounding protocol and trust assumptions are not included.

## Claim Boundaries

1. Supported claim: the patch hardens peer block validation by requiring parent continuity before advancing cross-check state.
2. Supported claim: fabricated or reordered chain data from a malicious peer is now more likely to be rejected.
3. Not supported: a proven resource-exhaustion bug with demonstrated remote DoS impact.
4. Not supported: a proven consensus-security break or full fake-chain acceptance beyond the downloader stage.
