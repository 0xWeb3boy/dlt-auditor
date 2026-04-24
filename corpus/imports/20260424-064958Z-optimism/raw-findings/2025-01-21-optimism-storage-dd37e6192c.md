---
case_id: case_20250121_dd37e6192c
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
impact_type:
  - state-integrity
source_quality: high
date: 2025-01-21
source_refs:
  - git:dd37e6192c37ed4c5b18df0269f065f378c495cc
  - "op-supervisor/supervisor/backend/db/logs/db.go:554"
  - "op-supervisor/supervisor/backend/db/fromda/update.go:148"
  - "op-supervisor/supervisor/backend/db/fromda/db.go:259"
  - "op-supervisor/supervisor/backend/db/fromda/update.go:13"
bug_class: insufficient-state-transition-validation
confidence: medium
tags:
  - infrastructure
  - storage
  - database
  - state-validation
  - block-identity
  - reorg-handling
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens correctness of `op-supervisor` database handling around rewinds and DA-derived block invalidation/replacement. The evidence supports a state-integrity fix for reorg or replacement edge cases, but it does not establish an exploitable vulnerability or a concrete security impact.

## Observed Patch Facts

1. In `op-supervisor/supervisor/backend/db/logs/db.go`, the patch replaces `// The block at headBlockNum itself is not removed.` with `// The block at newHead.Number itself is not removed.`.

2. In `op-supervisor/supervisor/backend/db/fromda/update.go`, the patch replaces `return fmt.Errorf("derived block %s conflicts with known derived block %s at same hei...` with `if invalidated != (common.Hash{}) {`.

3. In `op-supervisor/supervisor/backend/db/fromda/db.go`, the patch replaces `// Either one or both of the two entries will be an increment by 1` with `// Either one or both of the two entries will be an increment by 1.`.

4. In `op-supervisor/supervisor/backend/db/fromda/update.go`, the patch replaces `// If we don't have any entries yet, allow any block to start things off` with `return db.addLink(derivedFrom, derived, common.Hash{})`.

## Project Context

The changed code sits primarily in `op-supervisor/supervisor/backend/db/logs`, `op-supervisor/supervisor/backend/db`, `op-supervisor/supervisor/backend/db/fromda`, which anchors the finding in the `storage` area of the project. Historical context from `op-supervisor/supervisor/backend/db/fromda/update_test.go`, `op-supervisor/supervisor/backend/db/fromda/entry_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-supervisor/supervisor/backend/db/fromda/update_test.go`, `op-supervisor/supervisor/backend/db/fromda/entry_test.go`. The strongest project-level identifiers around this patch are `derived`, `block`, `types`, and `Hash`.

## Before/After Behavior

Before the patch, log rewind accepted only a block number and the shown code did not verify that the stored block at that height matched an expected hash before truncation. In the DA-derived path, same-height derived entries were either identical or a conflict, with no explicit invalidation/replacement flow shown. After the patch, rewind requires an `eth.BlockID` and checks the stored sealed block hash, the derived-link path carries an explicit `invalidated` hash and blocks further buildup on invalidated state, and traversal can surface `ErrAwaitReplacementBlock` until replacement is completed.

# Root Cause

The shown code handled some state transitions by height or implicit conflict checks without an explicit invalidation lifecycle tied to exact block identity. That could leave the supervisor DB in an inconsistent state during block replacement or rewind edge cases.

## Walkthrough

1. `logs.DB.Rewind` changed from `uint64` input to `eth.BlockID`, so callers now provide both number and hash.

2. The new rewind path seeks by number, reads the sealed block, and errors if the stored hash does not match the requested hash.

3. `AddDerived` now delegates to `addLink(..., invalidated)` rather than only appending a normal link.

4. `addLink` records whether an entry is invalidated, rejects an invalidated first entry, and rejects building on top of an already invalidated last entry.

5. In the same-height case, replacement is only accepted when the previous hash matches the explicitly supplied invalidated hash.

6. `ReplaceInvalidatedBlock` adds a dedicated replacement path instead of treating replacement as an ordinary append.

7. `FirstAfter` now documents and returns an error state when traversal reaches an invalidated entry awaiting replacement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supervisor/supervisor/backend/db/logs/db.go | 554 | rewind log DB to an exact L1 block identity; now checks hash as well as height before truncation |
| op-supervisor/supervisor/backend/db/fromda/update.go | 94 | enforces sequential derived-block linkage and only permits same-height replacement when the prior block is the explicitly invalidated one |
| op-supervisor/supervisor/backend/db/fromda/update.go | 12 | adds explicit invalidated-block replacement workflow for DA-derived entries |
| op-supervisor/supervisor/backend/db/fromda/db.go | 259 | iteration/query path now surfaces invalidated entries as needing replacement instead of treating them as normal progression |

## Code Snippets

## Snippet 1

Context: `op-supervisor/supervisor/backend/db/logs/db.go:554` (changes signature or replay validation logic)

Before
```go
// Rewind the database to remove any blocks after headBlockNum
// The block at headBlockNum itself is not removed.
func (db *DB) Rewind(newHeadBlockNum uint64) error {
	db.rwLock.Lock()
	defer db.rwLock.Unlock()
	// Even if the last fully-processed block matches headBlockNum,
	// we might still have trailing log events to get rid of.
```
After
```go
// Rewind the database to remove any blocks after headBlockNum
// The block at newHead.Number itself is not removed.
func (db *DB) Rewind(newHead eth.BlockID) error {
	db.rwLock.Lock()
	defer db.rwLock.Unlock()
	// Even if the last fully-processed block matches headBlockNum,
	// we might still have trailing log events to get rid of.
```

## Snippet 2

Context: `op-supervisor/supervisor/backend/db/fromda/update.go:148` (changes signature or replay validation logic)

Before
```go
// Same block height? Then it must be the same block.
		// I.e. we encountered an empty L1 block, and the same L2 block continues to be the last block that was derived from it.
		if lastDerived.Hash != derived.Hash {
			return fmt.Errorf("derived block %s conflicts with known derived block %s at same height: %w",
				derived, lastDerived, types.ErrConflict)
		}
	} else if lastDerived.Number+1 == derived.Number {
```
After
```go
// Same block height? Then it must be the same block.
		// I.e. we encountered an empty L1 block, and the same L2 block continues to be the last block that was derived from it.
		if invalidated != (common.Hash{}) {
			if lastDerived.Hash != invalidated {
				return fmt.Errorf("inserting block %s that invalidates %s at height %d, but expected %s", derived.Hash, invalidated, lastDerived.Number, lastDerived.Hash)
			}
		} else {
			if lastDerived.Hash != derived.Hash {
```

## Snippet 3

Context: `op-supervisor/supervisor/backend/db/fromda/db.go:259` (changes persisted or aggregate state handling)

Before
```go
// FirstAfter determines the next entry after the given pair of derivedFrom, derived.
// Either one or both of the two entries will be an increment by 1
func (db *DB) FirstAfter(derivedFrom, derived eth.BlockID) (nextDerivedFrom, nextDerived types.BlockSeal, err error) {
	db.rwLock.RLock()
	defer db.rwLock.RUnlock()
	selfIndex, selfLink, err := db.lookup(derivedFrom.Number, derived.Number)
	if err != nil {
```
After
```go
// FirstAfter determines the next entry after the given pair of derivedFrom, derived.
// Either one or both of the two entries will be an increment by 1.
// This may return types.ErrAwaitReplacementBlock if the entry was invalidated and needs replacement.
func (db *DB) FirstAfter(derivedFrom, derived eth.BlockID) (pair types.DerivedBlockSealPair, err error) {
	db.rwLock.RLock()
	defer db.rwLock.RUnlock()
	selfIndex, selfLink, err := db.lookup(derivedFrom.Number, derived.Number)
```

## Snippet 4

Context: `op-supervisor/supervisor/backend/db/fromda/update.go:13` (changes signature or replay validation logic)

Before
```go
db.rwLock.Lock()
	defer db.rwLock.Unlock()

	// If we don't have any entries yet, allow any block to start things off
	if db.store.Size() == 0 {
		link := LinkEntry{
			derivedFrom: types.BlockSeal{
				Hash:      derivedFrom.Hash,
```
After
```go
db.rwLock.Lock()
	defer db.rwLock.Unlock()
	return db.addLink(derivedFrom, derived, common.Hash{})
}

// ReplaceInvalidatedBlock replaces the current Invalidated block with the given replacement.
// The to-be invalidated hash must be provided for consistency checks.
func (db *DB) ReplaceInvalidatedBlock(replacementDerived eth.BlockRef, invalidated common.Hash) error {
```

# Fix Pattern

Tighten state-transition checks by requiring exact identity matches and by modeling invalidation/replacement as explicit fail-closed state instead of implicit overwrite behavior.

## How It Was Fixed

The fix adds hash validation to rewind operations, introduces explicit invalidation metadata and replacement handling for DA-derived entries, and makes iteration/reporting surface unresolved invalidated state instead of progressing as if the history were complete.

# Why It Matters

1. Reduces the chance of truncating or resuming from the wrong block at the same height.

2. Makes replacement of a derived block an explicit checked operation.

3. Prevents continued state construction on top of an invalidated entry.

4. Improves consistency handling for reorg or replacement edge cases.

# Evidence Notes

The strongest evidence is the `Rewind` signature change plus added sealed-block hash comparison in `op-supervisor/supervisor/backend/db/logs/db.go`, the new `invalidated` handling and `ReplaceInvalidatedBlock` path in `op-supervisor/supervisor/backend/db/fromda/update.go`, and the `ErrAwaitReplacementBlock` contract in `op-supervisor/supervisor/backend/db/fromda/db.go`. This supports a correctness/integrity hardening narrative. The provided material does not show attacker reachability, a demonstrated exploit, or a clearly established security boundary violation. Protocol security invariant: Persisted supervisor state should bind rewind and derivation transitions to exact block identities and should not continue past an invalidated derived entry until a checked replacement is installed. Verification notes: The patch does not by itself prove external attacker reachability. It does not show direct theft, privilege escalation, or memory-safety impact. It is not proven that consensus failure was exploitable on a live network rather than an operator correctness bug. The exact trigger source for invalidation or replacement is not shown in the provided diff. The patch clearly changes behavior in consensus-adjacent state handling. The evidence is sufficient for a correctness/integrity fix classification. The evidence is not sufficient to confirm a security vulnerability. Helper and test files appear supportive rather than the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-state-transition-validation`
Final confidence: `medium`
Final tags: `infrastructure, storage, database, state-validation, block-identity, reorg-handling`

The patch does not prove an exploitable vulnerability, but it does clearly harden security-sensitive chain-state handling. The code moves rewind logic from height-only to exact block identity checks, introduces explicit invalidation and checked replacement of derived blocks, and fails closed when traversal reaches invalidated state awaiting replacement. In a blockchain supervisor or validator-adjacent component, those are meaningful integrity protections, so this fits a conservative security-hardening classification rather than a confirmed security fix.

## Security Evidence

1. `Rewind` now requires `eth.BlockID` and verifies the stored sealed block hash before truncation.
2. Derived-link insertion now carries an explicit `invalidated` hash and rejects mismatched same-height replacement.
3. The DB refuses to build new state on top of an already invalidated entry.
4. Traversal can now return `ErrAwaitReplacementBlock`, making unresolved invalidated state explicit and fail-closed.
5. The changes affect consensus-adjacent block derivation and rewind behavior, not just tests or refactoring.

## Missing Evidence

1. No proof of external attacker reachability or control over the invalidation/rewind inputs.
2. No demonstrated exploit, incident, or concrete consensus failure caused by the old behavior.
3. No explicit security advisory, vulnerability reference, or attacker impact statement in the commit metadata.
4. No evidence that the pre-patch behavior was exploitable beyond correctness or operator-integrity failure.

## Claim Boundaries

1. Supported claim: the patch hardens block-identity and invalidation handling in supervisor state transitions.
2. Supported claim: the pre-patch code could accept ambiguous or incomplete state transitions during rewind/replacement edge cases.
3. Not supported: a confirmed exploitable vulnerability or real-world attacker path.
4. Not supported: direct theft, privilege escalation, memory corruption, or proven network-wide consensus compromise.
