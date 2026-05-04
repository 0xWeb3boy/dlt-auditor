---
case_id: case_20250127_9e729ab76c
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-01-27
source_refs:
  - git:9e729ab76cf15cdba734c09530cb4651136260c8
  - "eth/gasprice/feehistory.go:178"
  - "core/state/statedb.go:885"
  - "core/state/statedb.go:875"
  - "core/state/snapshot/snapshot.go:925"
bug_class: rpc-resource-control
impact_type:
  - availability
confidence: medium
tags:
  - rpc
  - resource-control
  - input-validation
  - fee-history
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded behavioral change is an added maxQueryLimit check for caller-provided rewardPercentiles in eth/gasprice/feehistory.go. This is plausibly resource-control hardening, but the provided evidence does not prove exploitability, denial of service, consensus impact, or another concrete security vulnerability. The StateDB changes appear to be copy-initialization refactoring, and the snapshot change is comment-only.

## Observed Patch Facts

1. In `eth/gasprice/feehistory.go`, the patch adds `if len(rewardPercentiles) > maxQueryLimit {`.

2. In `core/state/statedb.go`, the patch removes `// Deep copy the preimages occurred in the scope of block`.

3. In `core/state/statedb.go`, the patch replaces `// Deep copy the destruction markers.` with `// Deep copy the logs occurred in the scope of block`.

4. In `core/state/snapshot/snapshot.go`, the patch replaces `// DiskRoot is a external helper function to return the disk layer root.` with `// DiskRoot is an external helper function to return the disk layer root.`.

## Project Context

The changed code sits primarily in `eth/gasprice`, `core/state`, `core/state/snapshot`, which anchors the finding in the `storage` area of the project. Historical context from `core/state/statedb_test.go`, `core/state/state_object.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/gasprice/gasprice_test.go`, `core/state/trie_prefetcher.go`. The strongest project-level identifiers around this patch are `state`, `copy`, `Deep`, and `common`. Nearby tests or test-like files include `core/state/statedb_fuzz_test.go`.

## Before/After Behavior

Before the patch, the extracted FeeHistory code returned early for blocks < 1, then bounded blocks by oracle.maxCallBlockHistory, and later validated each rewardPercentiles value without any visible length check. After the patch, FeeHistory rejects rewardPercentiles arrays longer than maxQueryLimit before block truncation and per-percentile validation. In StateDB.Copy, copy metadata is initialized in the StateDB literal instead of through later explicit copy loops. In snapshot.go, only comment grammar changes are shown.

# Root Cause

The only supported root cause is that the supplied pre-patch FeeHistory snippet lacks a cardinality bound on the caller-controlled rewardPercentiles array. The evidence does not support claiming state corruption, consensus divergence, cryptographic failure, replay failure, authentication failure, or authorization bypass.

## Walkthrough

1. A caller supplies blocks and a rewardPercentiles array to Oracle.FeeHistory.

2. The function handles blocks < 1 with an early return.

3. Before the patch, the visible resource-control logic bounded only the block count, not the length of rewardPercentiles.

4. The function then iterated over rewardPercentiles to validate each value.

5. After the patch, rewardPercentiles arrays longer than maxQueryLimit are rejected with errInvalidPercentile before further processing.

6. The StateDB.Copy hunks move or consolidate copy bookkeeping and do not establish a separate security fix from the provided evidence.

7. The snapshot hunk is comment-only and has no behavioral security effect.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/gasprice/feehistory.go | 178 | Adds maxQueryLimit enforcement for caller-provided rewardPercentiles before fee history processing. |
| core/state/statedb.go | 818 | Initializes copied StateDB bookkeeping maps and cloned state-copy metadata. |
| core/state/statedb.go | 875 | Removes separate post-initialization copying of destruction markers and account/storage tracking in favor of constructor-time initialization. |
| core/state/statedb.go | 885 | Removes separate preimage copy loop because preimages are cloned during StateDB copy construction. |
| core/state/snapshot/snapshot.go | 925 | Comment grammar change only; no behavioral security role shown. |

## Code Snippets

## Snippet 1

Context: `eth/gasprice/feehistory.go:178` (changes bounds, limits, or capacity handling)

Before
```go
return common.Big0, nil, nil, nil, nil // returning with no data and no error means there are no retrievable blocks
	}
	if blocks > oracle.maxCallBlockHistory {
		log.Warn("Sanitizing fee history length", "requested", blocks, "truncated", oracle.maxCallBlockHistory)
```
After
```go
return common.Big0, nil, nil, nil, nil // returning with no data and no error means there are no retrievable blocks
	}
	if len(rewardPercentiles) > maxQueryLimit {
		return common.Big0, nil, nil, nil, fmt.Errorf("%w: over the query limit %d", errInvalidPercentile, maxQueryLimit)
	}
	if blocks > oracle.maxCallBlockHistory {
		log.Warn("Sanitizing fee history length", "requested", blocks, "truncated", oracle.maxCallBlockHistory)
```

## Snippet 2

Context: `core/state/statedb.go:885` (changes signature or replay validation logic)

Before
```go
state.logs[hash] = cpy
	}
	// Deep copy the preimages occurred in the scope of block
	for hash, preimage := range s.preimages {
		state.preimages[hash] = preimage
	}
	// Do we need to copy the access list and transient storage?
	// In practice: No. At the start of a transaction, these two lists are empty.
```
After
```go
state.logs[hash] = cpy
	}
	// Do we need to copy the access list and transient storage?
	// In practice: No. At the start of a transaction, these two lists are empty.
```

## Snippet 3

Context: `core/state/statedb.go:875` (changes persisted or aggregate state handling)

Before
```go
state.stateObjectsDirty[addr] = struct{}{}
	}
	// Deep copy the destruction markers.
	for addr, value := range s.stateObjectsDestruct {
		state.stateObjectsDestruct[addr] = value
	}
	// Deep copy the state changes made in the scope of block
	// along with their original values.
```
After
```go
state.stateObjectsDirty[addr] = struct{}{}
	}

	// Deep copy the logs occurred in the scope of block
```

## Snippet 4

Context: `core/state/snapshot/snapshot.go:925` (changes a sensitive control or state-update path)

Before
```go
}

// DiskRoot is a external helper function to return the disk layer root.
func (t *Tree) DiskRoot() common.Hash {
	t.lock.Lock()
```
After
```go
}

// DiskRoot is an external helper function to return the disk layer root.
func (t *Tree) DiskRoot() common.Hash {
	t.lock.Lock()
```

# Fix Pattern

Add an early cardinality check for a caller-controlled RPC array parameter using an existing query limit before repeated processing continues.

## How It Was Fixed

eth/gasprice/feehistory.go now checks len(rewardPercentiles) > maxQueryLimit near the start of Oracle.FeeHistory and returns errInvalidPercentile when exceeded. StateDB.Copy was refactored to clone or copy bookkeeping fields during StateDB construction. The snapshot change only corrects a comment.

# Why It Matters

1. Bounds a caller-controlled RPC input.

2. Reduces risk of oversized fee-history requests causing excess work.

3. Security impact is plausible but not proven by the supplied evidence.

4. Avoids treating StateDB refactoring as a demonstrated vulnerability.

5. Excludes comment-only cleanup from security classification.

# Evidence Notes

Strongest evidence is eth/gasprice/feehistory.go line 178 adding len(rewardPercentiles) > maxQueryLimit. The before snippet shows no equivalent length check, only block-count truncation and later per-value percentile validation. StateDB.Copy after-context shows constructor-time cloning/copying of accounts, storages, stateObjectsDestruct, and preimages, while before-context shows later explicit copying; this supports refactor/cleanup, not a demonstrated security flaw. snapshot.go only changes comment grammar. Protocol security invariant: Public RPC handlers should bound caller-controlled collection inputs before repeated validation or response computation. The supplied evidence shows this invariant being added for FeeHistory rewardPercentiles, but does not establish an exploitable vulnerability or concrete denial-of-service condition. Verification notes: No exploitability is proven by the patch evidence alone. No consensus divergence or state corruption attack is demonstrated from the StateDB copy refactor. No authentication, authorization, cryptographic verification, or replay-protection invariant is shown as fixed. The snapshot hunk is non-security comment cleanup. The fee history issue is best bounded as resource-control hardening, not confirmed remote denial of service. No exploitability evidence is provided. No concrete denial-of-service threshold or benchmark is provided. No test evidence is included for oversized rewardPercentiles. No consensus or state-corruption impact is established. Classified as unclear rather than a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rpc-resource-control`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `rpc, resource-control, input-validation, fee-history, availability`

The strongest supported security-relevant change is the new maxQueryLimit check on caller-provided rewardPercentiles in FeeHistory, which bounds a potentially exposed RPC collection input before repeated processing. The evidence supports resource-control hardening, not a proven exploitable denial of service and not state corruption. The StateDB hunks look like copy/refactor cleanup from the supplied context, and the snapshot hunk is comment-only.

## Security Evidence

1. FeeHistory now rejects rewardPercentiles arrays longer than maxQueryLimit.
2. The bounded value is caller-provided input to a fee history API path.
3. The change is explicitly resource-control behavior: cardinality limiting before further validation and processing.

## Missing Evidence

1. No exploit, benchmark, or concrete denial-of-service threshold is provided.
2. No advisory, CVE, test, or commit message detail confirms a vulnerability.
3. No evidence supports consensus divergence, state corruption, cryptographic failure, or replay failure.
4. StateDB changes are not shown to fix an externally triggerable security issue.

## Claim Boundaries

1. Classify only as RPC resource-control hardening, not a confirmed security fix.
2. Do not retain the original state-corruption or state-integrity framing.
3. Do not treat the comment-only snapshot change as security evidence.
4. Do not claim exploitability beyond oversized input being newly bounded.
