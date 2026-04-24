---
case_id: case_20250110_77ece638bd
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-01-10
source_refs:
  - git:77ece638bd1103ee878fceaaf7e69de47e316032
  - "op-supervisor/supervisor/backend/db/query.go:211"
  - "op-supervisor/supervisor/backend/db/logs/db.go:316"
  - "op-supervisor/supervisor/backend/db/logs/iterator.go:122"
  - "op-supervisor/supervisor/backend/cross/unsafe_start.go:69"
bug_class: insufficient-validation
impact_type:
  - protocol-integrity
confidence: medium
tags:
  - protocol-validation
  - timestamp-check
  - consensus-sensitive
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly tightens a timestamp-related correctness invariant in supervisor log inclusion checks, but the provided evidence does not establish a concrete security vulnerability. It is best characterized as a protocol-validation logic fix with unclear security impact.

## Observed Patch Facts

1. In `op-supervisor/supervisor/backend/db/query.go`, the patch replaces `func (db *ChainsDB) Check(chain types.ChainID, blockNum uint64, logIdx uint32, logHas...` with `func (db *ChainsDB) Check(chain types.ChainID, blockNum uint64, timestamp uint64, log...`.

2. In `op-supervisor/supervisor/backend/db/logs/db.go`, the patch replaces `h, n, _ := iter.SealedBlock()` with `h, n, ok := iter.SealedBlock()`.

3. In `op-supervisor/supervisor/backend/db/logs/iterator.go`, the patch adds `// don't rewind to the snapshot if the error is ErrStop`.

4. In `op-supervisor/supervisor/backend/cross/unsafe_start.go`, the patch adds `if includedIn.Timestamp != msg.Timestamp {`.

## Project Context

The changed code sits primarily in `op-supervisor/supervisor/backend/db`, `op-supervisor/supervisor/backend`, `op-supervisor/supervisor/backend/db/logs`, which anchors the finding in the `storage` area of the project. Historical context from `op-supervisor/supervisor/backend/db/db.go`, `op-supervisor/supervisor/backend/cross/unsafe_start_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-supervisor/supervisor/backend/db/db.go`, `op-supervisor/supervisor/backend/cross/unsafe_start_test.go`. The strongest project-level identifiers around this patch are `types`, `includedIn`, `block`, and `BlockSeal`.

## Before/After Behavior

Before the patch, `ChainsDB.Check` delegated to `logDB.Contains` without supplying or validating an expected timestamp. After the patch, `Check` accepts a `timestamp` argument, compares it to `includedIn.Timestamp`, and returns a conflict on mismatch. The patch also changes iterator handling so `ErrStop` preserves the matched state and `Contains` now errors if traversal stopped without an actual sealed block.

# Root Cause

The validation path relied on an incomplete lookup contract: log inclusion was treated as sufficiently identified by block number, log index, and log hash, while timestamp was also part of the surrounding ordering/safety logic. Separately, iterator stop handling could leave ambiguity about whether the returned `BlockSeal` was the intended sealed block.

## Walkthrough

1. `CrossUnsafeHazards` checks older executing messages by asking a dependency layer to confirm the initiating log and its inclusion context.

2. Before the change, `ChainsDB.Check` returned `logDB.Contains(blockNum, logIdx, logHash)` directly, so no expected timestamp was part of that helper contract.

3. After the change, `ChainsDB.Check` takes `timestamp`, captures the returned `BlockSeal`, and rejects mismatched timestamps.

4. `unsafe_start.go` also adds an explicit `includedIn.Timestamp != msg.Timestamp` conflict check, showing timestamp is part of the intended invariant.

5. `iterator.go` now preserves iterator state on `ErrStop` instead of rewinding, so the stop position remains available to the caller.

6. `db.go` now verifies that `iter.SealedBlock()` actually succeeded before constructing the returned `BlockSeal`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supervisor/supervisor/backend/db/query.go | 211 | timestamp-aware log inclusion check used by supervisor validation |
| op-supervisor/supervisor/backend/cross/unsafe_start.go | 69 | cross-unsafe hazard path that depends on the checked block timestamp invariant |
| op-supervisor/supervisor/backend/db/logs/iterator.go | 122 | iterator stop-state handling so lookup returns the actual matched sealed block |
| op-supervisor/supervisor/backend/db/logs/db.go | 316 | log containment lookup that constructs the returned BlockSeal after traversal stops |
| op-supervisor/supervisor/backend/cross/safe_start.go | 5 | cross-safe dependency contract updated to require timestamp-bound checks |

## Code Snippets

## Snippet 1

Context: `op-supervisor/supervisor/backend/db/query.go:211` (changes signature or replay validation logic)

Before
```go
// Check calls the underlying logDB to determine if the given log entry exists at the given location.
// If the block-seal of the block that includes the log is known, it is returned. It is fully zeroed otherwise, if the block is in-progress.
func (db *ChainsDB) Check(chain types.ChainID, blockNum uint64, logIdx uint32, logHash common.Hash) (includedIn types.BlockSeal, err error) {
	logDB, ok := db.logDBs.Get(chain)
	if !ok {
		return types.BlockSeal{}, fmt.Errorf("%w: %v", types.ErrUnknownChain, chain)
	}
	return logDB.Contains(blockNum, logIdx, logHash)
```
After
```go
// Check calls the underlying logDB to determine if the given log entry exists at the given location.
// If the block-seal of the block that includes the log is known, it is returned. It is fully zeroed otherwise, if the block is in-progress.
func (db *ChainsDB) Check(chain types.ChainID, blockNum uint64, timestamp uint64, logIdx uint32, logHash common.Hash) (includedIn types.BlockSeal, err error) {
	logDB, ok := db.logDBs.Get(chain)
	if !ok {
		return types.BlockSeal{}, fmt.Errorf("%w: %v", types.ErrUnknownChain, chain)
	}
	includedIn, err = logDB.Contains(blockNum, logIdx, logHash)
```

## Snippet 2

Context: `op-supervisor/supervisor/backend/db/logs/db.go:316` (changes a sensitive control or state-update path)

Before
```go
}
	if errors.Is(err, types.ErrStop) {
		h, n, _ := iter.SealedBlock()
		timestamp, _ := iter.SealedTimestamp()
		return types.BlockSeal{
```
After
```go
}
	if errors.Is(err, types.ErrStop) {
		h, n, ok := iter.SealedBlock()
		if !ok {
			return types.BlockSeal{}, fmt.Errorf("iterator stopped but no sealed block found")
		}
		timestamp, _ := iter.SealedTimestamp()
		return types.BlockSeal{
```

## Snippet 3

Context: `op-supervisor/supervisor/backend/db/logs/iterator.go:122` (changes a sensitive control or state-update path)

Before
```go
}
		if err := fn(&i.current); err != nil {
			i.current = snapshot
			return err
```
After
```go
}
		if err := fn(&i.current); err != nil {
			// don't rewind to the snapshot if the error is ErrStop
			if errors.Is(err, types.ErrStop) {
				return err
			}
			i.current = snapshot
			return err
```

## Snippet 4

Context: `op-supervisor/supervisor/backend/cross/unsafe_start.go:69` (changes a sensitive control or state-update path)

Before
```go
return nil, fmt.Errorf("msg %s included in non-cross-unsafe block %s: %w", msg, includedIn, err)
			}
		} else if msg.Timestamp == candidate.Timestamp {
			// If timestamp is equal: we have to inspect ordering of individual
```
After
```go
return nil, fmt.Errorf("msg %s included in non-cross-unsafe block %s: %w", msg, includedIn, err)
			}
			if includedIn.Timestamp != msg.Timestamp {
				return nil, fmt.Errorf("executing msg %s exists, but has different timestamp than block %s: %w", msg, includedIn, types.ErrConflict)
			}
		} else if msg.Timestamp == candidate.Timestamp {
			// If timestamp is equal: we have to inspect ordering of individual
```

# Fix Pattern

Strengthen invariant checks by passing all required identity fields through helper APIs and failing closed when reconstructed state does not exactly match the expected sealed-block context.

## How It Was Fixed

The fix threads `timestamp` through the `Check` interface, rejects mismatched `BlockSeal` timestamps, preserves iterator position on `ErrStop`, and refuses to return a seal when traversal did not actually end on a sealed block.

# Why It Matters

1. It prevents supervisor validation from accepting a partial match that omits a timestamp check.

2. It makes the returned inclusion context more trustworthy by tying it to the actual sealed block reached by traversal.

3. It improves protocol-validation correctness in a safety-sensitive path, even though exploitability is not shown here.

# Evidence Notes

The strongest evidence is the added timestamp parameter and mismatch rejection in `op-supervisor/supervisor/backend/db/query.go`, the explicit timestamp conflict check in `op-supervisor/supervisor/backend/cross/unsafe_start.go`, and the iterator/`SealedBlock` handling changes in `op-supervisor/supervisor/backend/db/logs/iterator.go` and `op-supervisor/supervisor/backend/db/logs/db.go`. The commit message and test updates indicate a timestamp invariant fix. However, the provided material does not show attacker control, demonstrated bypass, consensus failure, or other concrete security impact. Protocol security invariant: When the supervisor validates an executing message against stored logs, the returned inclusion context should correspond to the exact sealed block expected by the protocol, including the expected timestamp, rather than only matching block number, log index, and log hash. Verification notes: The patch does not by itself prove remote exploitability. The patch does not prove fund loss, privilege escalation, or arbitrary state corruption. It is not proven whether the pre-fix behavior was reachable from untrusted inputs in production. The evidence supports incorrect validation of cross-chain message/block relationships, not a cryptographic break. The iterator fixes may also prevent false negatives or internal inconsistencies; the patch alone does not quantify exact impact. The patch supports a correctness/invariant fix, not a proven exploitable vulnerability. No direct evidence here shows the pre-fix behavior was reachable from adversarial input. No concrete impact such as fund loss, privilege escalation, or chain compromise is established by the supplied snippets. Tests are mentioned in commit context, but their contents are not provided in enough detail to prove security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-validation`
Final impact type: `protocol-integrity`
Final confidence: `medium`
Final tags: `protocol-validation, timestamp-check, consensus-sensitive`

The patch clearly tightens validation in a security-sensitive supervisor path by binding log inclusion checks to the expected timestamp and by failing closed when iterator state cannot prove a sealed block. That supports treating this as security hardening for protocol-integrity checks. However, the supplied evidence does not demonstrate a concrete exploitable vulnerability, attacker-controlled trigger, or actual corruption/compromise, so it should not be elevated to a confirmed security fix.

## Security Evidence

1. `ChainsDB.Check` now requires an expected `timestamp` and rejects mismatched `includedIn.Timestamp`.
2. `CrossUnsafeHazards` adds an explicit conflict when the located block timestamp differs from the message timestamp.
3. Iterator handling preserves stop-state on `ErrStop`, avoiding loss of the matched sealed-block position.
4. `Contains` now errors if traversal stops without a real sealed block, removing an ambiguous success path.
5. Commit metadata and tests describe a timestamp invariant fix in supervisor validation logic.

## Missing Evidence

1. No proof that untrusted or adversarial input could reach and exploit the pre-fix behavior.
2. No demonstrated consensus break, fund loss, privilege gain, or remote attack path.
3. No evidence that the old behavior was used to bypass authorization or forge messages in production.
4. Test details are not specific enough to prove concrete exploitability.

## Claim Boundaries

1. The patch supports a claim of stronger protocol/supervisor validation, not a proven exploitable bug.
2. It should not be labeled as `state-corruption` from the provided diff alone.
3. It supports retention as `security-hardening`, not as a confirmed `security-fix`.
