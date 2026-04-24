---
case_id: case_20250314_d6a49f70d3
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-03-14
source_refs:
  - git:d6a49f70d3ba69a6d917eb61e4c023dd6d8b78ed
  - "op-supervisor/supervisor/backend/db/logs/db.go:294"
  - "op-supervisor/supervisor/backend/db/logs/db.go:327"
  - "op-supervisor/supervisor/backend/db/query.go:419"
  - "op-supervisor/supervisor/types/types.go:217"
bug_class: incomplete-verification-binding
impact_type:
  - verification-bypass-risk
confidence: medium
tags:
  - supervisor
  - verification
  - checksum
  - access-list
  - timestamp-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens `op-supervisor` verification logic by replacing a narrower log-hash check with a derived checksum over more fields and by adding explicit timestamp/timeout access checks. That is evidence of validation hardening, but the provided diff does not establish that the prior behavior was an exploitable vulnerability rather than an incompleteness or protocol-correctness cleanup.

## Observed Patch Facts

1. In `op-supervisor/supervisor/backend/db/logs/db.go`, the patch replaces `evtHash, iter, err := db.findLogInfo(blockNum, logIdx)` with `entryLogHash, iter, err := db.findLogInfo(blockNum, logIdx)`.

2. In `op-supervisor/supervisor/backend/db/logs/db.go`, the patch replaces `// construct a block seal with the found data now that we know it's correct` with `entryChecksum := types.ChecksumArgs{`.

3. In `op-supervisor/supervisor/backend/db/query.go`, the patch replaces `// Safest returns the strongest safety level that can be guaranteed for the given log...` with `func (db *ChainsDB) IteratorStartingAt(chain eth.ChainID, sealedNum uint64, logIndex...`.

4. In `op-supervisor/supervisor/types/types.go`, the patch replaces `type executingDescriptorMarshaling struct {` with `// Timeout, requests verification to still hold at Timestamp+Timeout (incl.). Default...`.

## Project Context

The changed code sits primarily in `op-supervisor/supervisor/backend/db/logs`, `op-supervisor/supervisor/backend/db`, `op-supervisor/supervisor/backend`, which anchors the finding in the `storage` area of the project. Historical context from `op-supervisor/supervisor/types/types_test.go`, `op-supervisor/supervisor/backend/db/logs/state.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-supervisor/supervisor/types/types_test.go`, `op-supervisor/supervisor/backend/db/logs/state.go`. The strongest project-level identifiers around this patch are `types`, `blockNum`, `logIdx`, and `Timestamp`.

## Before/After Behavior

Before the patch, the shown `Contains` path retrieved a stored log hash and compared it to an expected hash value, then continued once block/timestamp checks passed. After the patch, the same path derives a checksum from block number, log index, timestamp, chain ID, and stored log hash, and rejects the query unless that checksum matches `query.Checksum`. Separately, `ExecutingDescriptor` now carries `Timeout` and an `AccessCheck` method that enforces timestamp ordering rules.

# Root Cause

The shown code suggests earlier verification was bound to a narrower identifier than the newer checksum-based scheme, so the likely issue was incomplete context binding in verification. However, the evidence does not show a concrete failing case, attacker-controlled input path, or demonstrated security impact.

## Walkthrough

1. `Contains(query types.ContainsQuery)` still locates the requested log via `db.findLogInfo(blockNum, logIdx)`.

2. The removed snippet shows an earlier comparison against a hash value (`evtHash` versus an expected hash).

3. The patched code keeps the timestamp consistency check before acceptance.

4. After that, it computes `entryChecksum` from `BlockNumber`, `LogIndex`, `Timestamp`, `ChainID`, and `LogHash`.

5. The function now returns a conflict unless that derived checksum equals `query.Checksum`.

6. `ExecutingDescriptor` also gained `Timeout` plus `AccessCheck(...)`, which adds explicit temporal validation semantics.

7. `IteratorStartingAt` in `db/query.go` looks like supporting plumbing, not independent evidence of a vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supervisor/supervisor/backend/db/logs/db.go | 279 | core log-inclusion verification path used to answer `Contains` queries for initiating events |
| op-supervisor/supervisor/backend/db/logs/db.go | 327 | new checksum binding of chain/block/log/timestamp/hash before accepting a query result |
| op-supervisor/supervisor/types/types.go | 216 | execution descriptor access-window semantics and timestamp/timeout invariant enforcement |
| op-supervisor/supervisor/backend/db/query.go | 409 | database traversal entrypoint supporting log/access validation state lookup |

## Code Snippets

## Snippet 1

Context: `op-supervisor/supervisor/backend/db/logs/db.go:294` (changes signature or replay validation logic)

Before
```go
}

	evtHash, iter, err := db.findLogInfo(blockNum, logIdx)
	if err != nil {
		return types.BlockSeal{}, err // may be ErrConflict if the block does not have as many logs
	}
	db.log.Trace("Found initiatingEvent", "blockNum", blockNum, "logIdx", logIdx, "hash", evtHash)
	// Found the requested block and log index, check if the hash matches
```
After
```go
}

	entryLogHash, iter, err := db.findLogInfo(blockNum, logIdx)
	if err != nil {
		return types.BlockSeal{}, err // may be ErrConflict if the block does not have as many logs
	}
	db.log.Trace("Found initiatingEvent", "blockNum", blockNum, "logIdx", logIdx, "hash", entryLogHash)
	// Now find the block seal after the log, to identify where the log was included in.
```

## Snippet 2

Context: `op-supervisor/supervisor/backend/db/logs/db.go:327` (changes signature or replay validation logic)

Before
```go
return types.BlockSeal{}, fmt.Errorf("timestamp mismatch: expected %d, got %d %w", timestamp, t, types.ErrConflict)
		}
		// construct a block seal with the found data now that we know it's correct
		return types.BlockSeal{
```
After
```go
return types.BlockSeal{}, fmt.Errorf("timestamp mismatch: expected %d, got %d %w", timestamp, t, types.ErrConflict)
		}
		entryChecksum := types.ChecksumArgs{
			BlockNumber: n,
			LogIndex:    logIdx,
			Timestamp:   t,
			ChainID:     db.chainID,
			LogHash:     entryLogHash,
```

## Snippet 3

Context: `op-supervisor/supervisor/backend/db/query.go:419` (changes a consensus- or validator-sensitive branch)

Before
```go
}

// Safest returns the strongest safety level that can be guaranteed for the given log entry.
// it assumes the log entry has already been checked and is valid, this function only checks safety levels.
// Safety levels are assumed to graduate from LocalUnsafe to LocalSafe to CrossUnsafe to CrossSafe, with Finalized as the strongest.
func (db *ChainsDB) Safest(chainID eth.ChainID, blockNum uint64, index uint32) (safest types.SafetyLevel, err error) {
	if finalized, err := db.Finalized(chainID); err == nil {
		if finalized.Number >= blockNum {
```
After
```go
}

func (db *ChainsDB) IteratorStartingAt(chain eth.ChainID, sealedNum uint64, logIndex uint32) (logs.Iterator, error) {
	logDB, ok := db.logDBs.Get(chain)
```

## Snippet 4

Context: `op-supervisor/supervisor/types/types.go:217` (changes an authorization or privilege gate)

Before
```go
// Timestamp is the timestamp of the executing message
	Timestamp uint64
}

type executingDescriptorMarshaling struct {
	Timestamp hexutil.Uint64 `json:"timestamp"`
}
```
After
```go
// Timestamp is the timestamp of the executing message
	Timestamp uint64

	// Timeout, requests verification to still hold at Timestamp+Timeout (incl.). Defaults to 0.
	// I.e. Timestamp is used as lower-bound validity, and Timeout defines the span to the upper-bound.
	Timeout uint64
}
```

# Fix Pattern

Tighten verification by binding acceptance to more complete context and by making temporal validity checks explicit.

## How It Was Fixed

The patch changes the acceptance condition in the log containment path from a direct hash comparison to a checksum comparison over multiple contextual fields, and it adds explicit access-window checking through `ExecutingDescriptor.Timeout` and `AccessCheck`. This makes validation stricter and more explicit.

# Why It Matters

1. It reduces the chance that a partially matched log reference is treated as valid.

2. It makes timestamp-based access assumptions explicit in code.

3. It improves integrity checking in a sensitive supervisor verification path.

4. The supplied evidence still does not prove real-world exploitability or impact.

# Evidence Notes

Direct evidence is limited to the shown diff hunks. The strongest support is in `op-supervisor/supervisor/backend/db/logs/db.go`, where a narrower hash check is replaced with a checksum over several fields, and in `op-supervisor/supervisor/types/types.go`, where `Timeout` and `AccessCheck` add explicit temporal checks. The provided material does not show the full old/new query types, the caller behavior, or a failing scenario demonstrating that the old logic caused a security boundary bypass. Protocol security invariant: Verification of an initiating log or executing access condition should be bound to the full checked context and reject mismatched timestamp/context data before returning success. Verification notes: The patch does not by itself prove a practical exploit path or attacker-controlled checksum forgery. The patch does not prove consensus breakage, fund loss, or privilege escalation end-to-end. `IteratorStartingAt` exposure in `db/query.go` may be supporting plumbing rather than the root security fix. The timeout default/serialization update could partly be compatibility cleanup; only the access-window checks are clearly security-relevant from the shown diff. No concrete exploit path is shown in the provided evidence. No end-to-end test or bug report is included to prove the old behavior was vulnerable. The change is best supported as verification hardening or correctness tightening, not a confirmed vulnerability fix. Helper/plumbing changes such as `IteratorStartingAt` should not be treated as the root cause from the provided diff alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incomplete-verification-binding`
Final impact type: `verification-bypass-risk`
Final confidence: `medium`
Final tags: `supervisor, verification, checksum, access-list, timestamp-validation`

The patch clearly tightens a security-sensitive verification path: `Contains` moves from accepting a narrower log-hash match to requiring a checksum bound to block number, log index, timestamp, chain ID, and log hash, and `ExecutingDescriptor` gains explicit timeout and timestamp-window checks. That supports classifying the change as security hardening, because it removes acceptance of less-context-bound or temporally invalid inputs in an access-list/verification flow. The evidence does not, however, prove that the old behavior was exploitable or that a concrete security incident was fixed end to end.

## Security Evidence

1. `Contains` now derives and verifies a checksum over multiple contextual fields instead of relying on a narrower match.
2. Checksum mismatch returns `ErrConflict`, indicating stricter rejection of inconsistent query context.
3. `ExecutingDescriptor` adds `Timeout` plus `AccessCheck`, enforcing temporal validity constraints for access-list verification.
4. The touched code is in supervisor verification and access-list handling, which is a security-sensitive control path.

## Missing Evidence

1. No concrete exploit, failing test, advisory, or bug report shows the old logic could be abused.
2. No full before/after caller flow is shown to prove attacker-controlled input could bypass intended checks.
3. No evidence ties the change to privilege escalation, fund loss, consensus failure, or real-world compromise.

## Claim Boundaries

1. Evidence supports stricter validation and context binding, not a confirmed exploitable vulnerability.
2. This should not be labeled as state corruption from the supplied patch alone.
3. `IteratorStartingAt` appears to be supporting plumbing, not independent security proof.
4. The safest supported corpus entry is security hardening around verification and temporal access checks.
