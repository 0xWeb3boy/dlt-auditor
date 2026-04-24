---
case_id: case_20260318_b1829ef95
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2026-03-18
source_refs:
  - git:b1829ef952f432928d4204a3e14fcd9a0b643de0
  - "eth/filters/api.go:58"
  - "eth/filters/bor_api.go:40"
  - "eth/filters/api.go:524"
  - "eth/filters/api.go:609"
bug_class: resource-exhaustion-hardening
impact_type:
  - availability
confidence: medium
tags:
  - rpc
  - resource-limits
  - availability
  - log-filters
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The visible patch adds and broadens range checks in RPC log/filter handlers, which is consistent with availability hardening around expensive historical log scans. The code supports a correctness/resource-control fix, but the provided evidence does not establish an actual security vulnerability or exploit path.

## Observed Patch Facts

1. In `eth/filters/api.go`, the patch replaces `// filter is a helper struct that holds meta information over the filter type` with `// resolveBlockNumForRangeCheck converts a raw block number (which may be a negative`.

2. In `eth/filters/bor_api.go`, the patch replaces `// Construct the range filter` with `if begin > 0 && end > 0 && begin > end {`.

3. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

4. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

## Project Context

The changed code sits primarily in `eth/filters`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/filters/filter_system_test.go`, `eth/filters/filter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/filters/filter_system_test.go`, `eth/filters/filter.go`. The strongest project-level identifiers around this patch are `head`, `begin`, `filter`, and `crit`.

## Before/After Behavior

Before the change, the shown `GetLogs`, `GetFilterLogs`, and Bor `GetBorBlockLogs` paths proceeded to range-filter construction without the newly shown `checkBlockRangeLimit(...)` calls, and the Bor path snippet also lacked the explicit `begin > end` rejection. After the change, these handlers fetch the current head, call `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` before constructing range filters, and `eth/filters/api.go` adds `resolveBlockNumForRangeCheck` so symbolic negative RPC block tags can be converted to concrete heights for limit arithmetic while preserving original filter semantics.

# Root Cause

The visible issue is missing or inconsistent pre-construction validation for block-range log queries in multiple RPC paths. The commit subject suggests a separate config pass-through problem for the range-limit setting, but that wiring is not shown in the supplied evidence.

## Walkthrough

1. `eth/filters/api.go` adds `resolveBlockNumForRangeCheck`, with comments describing how symbolic negative block numbers are normalized for range-limit arithmetic.

2. `GetLogs` now reads the current head and calls `checkBlockRangeLimit(...)` before `NewRangeFilter(...)` is created.

3. `GetFilterLogs` now applies the same head lookup and `checkBlockRangeLimit(...)` before reconstructing a range filter from stored criteria.

4. `eth/filters/bor_api.go` now rejects reversed positive ranges with `errInvalidBlockRange` and also applies `checkBlockRangeLimit(...)` before constructing the Bor range filter.

5. The repeated placement of these checks shows a new invariant at RPC entry points, but the evidence does not prove concrete attacker-triggered exhaustion or deployment exposure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/filters/api.go | 58 | normalizes symbolic RPC block numbers for range-limit enforcement |
| eth/filters/api.go | 475 | main `GetLogs` RPC path now rejects excessive historical ranges before creating range filters |
| eth/filters/api.go | 577 | `GetFilterLogs` path now reapplies range-limit checks when serving stored log filters |
| eth/filters/bor_api.go | 19 | Bor-specific log RPC path now validates range ordering and enforces configured range limits |

## Code Snippets

## Snippet 1

Context: `eth/filters/api.go:58` (changes bounds, limits, or capacity handling)

Before
```go
)

// filter is a helper struct that holds meta information over the filter type
// and associated subscription in the event system.
```
After
```go
)

// resolveBlockNumForRangeCheck converts a raw block number (which may be a negative
// sentinel for symbolic values like "latest", "earliest", etc.) to a concrete
// non-negative height suitable for range arithmetic. It is used only for the
// range-limit guard; the actual filter still receives the original sentinel value.
//   - earliest (-5) → 0
//   - all other sentinels (latest, safe, finalized, pending) → head
```

## Snippet 2

Context: `eth/filters/bor_api.go:40` (changes a sensitive control or state-update path)

Before
```go
end = crit.ToBlock.Int64()
		}
		// Construct the range filter
		filter = NewBorBlockLogsRangeFilter(api.sys.backend, borConfig, begin, end, crit.Addresses, crit.Topics)
```
After
```go
end = crit.ToBlock.Int64()
		}
		if begin > 0 && end > 0 && begin > end {
			return nil, errInvalidBlockRange
		}
		head := api.sys.backend.CurrentHeader().Number.Uint64()
		if err := checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit); err != nil {
			return nil, err
```

## Snippet 3

Context: `eth/filters/api.go:524` (changes a sensitive control or state-update path)

Before
```go
return nil, &history.PrunedHistoryError{}
		}
		// Construct the range filter
		filter = api.sys.NewRangeFilter(begin, end, crit.Addresses, crit.Topics)
```
After
```go
return nil, &history.PrunedHistoryError{}
		}
		head := api.sys.backend.CurrentHeader().Number.Uint64()
		if err := checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit); err != nil {
			return nil, err
		}
		// Construct the range filter
		filter = api.sys.NewRangeFilter(begin, end, crit.Addresses, crit.Topics)
```

## Snippet 4

Context: `eth/filters/api.go:609` (changes a sensitive control or state-update path)

Before
```go
end = f.crit.ToBlock.Int64()
		}
		// Construct the range filter
		filter = api.sys.NewRangeFilter(begin, end, f.crit.Addresses, f.crit.Topics)
```
After
```go
end = f.crit.ToBlock.Int64()
		}
		head := api.sys.backend.CurrentHeader().Number.Uint64()
		if err := checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit); err != nil {
			return nil, err
		}
		// Construct the range filter
		filter = api.sys.NewRangeFilter(begin, end, f.crit.Addresses, f.crit.Topics)
```

# Fix Pattern

Add explicit validation gates at RPC entry points so malformed or oversized ranges are rejected before historical scan work is started.

## How It Was Fixed

The visible fix inserts `checkBlockRangeLimit(...)` into the main log query path, the stored-filter replay path, and the Bor-specific log query path, and adds helper logic to normalize symbolic block numbers for range-limit arithmetic. The broader `--rpc.rangelimit` flag/config pass-through mentioned in the commit metadata is plausible support work, but it is not directly shown in the provided hunks.

# Why It Matters

1. Historical log queries can be costly, so bounding their range is operationally important.

2. Applying checks in multiple handlers reduces gaps between different query entry points.

3. Symbolic block tags need explicit handling for any arithmetic-based range guard.

4. The visible evidence supports hardening/correctness more clearly than a proven security fix.

# Evidence Notes

Direct evidence shows new range-limit enforcement and block-range validation in `eth/filters/api.go` and `eth/filters/bor_api.go`, plus helper logic for symbolic block numbers. The file list and commit subject imply CLI/config plumbing for `--rpc.rangelimit`, but those wiring changes were not included in the supplied code excerpts. No benchmark, incident, exposure model, or demonstrated denial-of-service path is provided. Protocol security invariant: Range-based log/filter RPC handlers should validate block-range ordering and enforce the configured maximum scan span before constructing range filters, including when symbolic block tags are used. Verification notes: The patch does not prove these RPC methods were exposed to untrusted callers in every deployment. The patch shows availability/resource controls, not confidentiality or integrity impact. The exact prior config pass-through bug is implied by the commit subject, not fully shown in the provided hunks. No concrete CPU, memory, or disk exhaustion measurements are shown. The patch does not show consensus-rule or on-chain state corruption risk. The code change clearly strengthens range checking in RPC filter handlers. The provided evidence does not establish real-world exploitability or attacker reachability. The config pass-through aspect is only partially evidenced by commit metadata, not by visible hunks. Treating this as definitively security-relevant would overstate what the patch alone proves. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion-hardening`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `rpc, resource-limits, availability, log-filters`

The supplied patch consistently adds block-range validation and configured range-limit enforcement to multiple RPC log/filter entry points, including handling symbolic block tags for limit arithmetic. That is credible availability-focused security hardening because it reduces the risk of expensive unbounded historical scans through externally reachable RPC methods. However, the evidence does not prove a concrete exploitable vulnerability, prior bypass in all deployments, or observed denial-of-service impact, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Adds `checkBlockRangeLimit(...)` before constructing range filters in `GetLogs`.
2. Adds the same range-limit guard in `GetFilterLogs`, closing an alternate query path.
3. Adds range ordering validation and range-limit enforcement in Bor log RPC handling.
4. Introduces normalization of symbolic negative block numbers specifically for range-limit checks.
5. Commit subject and touched CLI/config files indicate intentional RPC range-limit enforcement plumbing.

## Missing Evidence

1. No proof that the affected RPC methods were exposed to untrusted callers in typical deployments.
2. No demonstrated CPU, memory, disk, or latency exhaustion from the pre-patch behavior.
3. No evidence of an incident, advisory, CVE, or exploit scenario.
4. No visible hunk showing the exact prior config pass-through bug or a bypass being fixed.

## Claim Boundaries

1. Supported claim: the commit hardens RPC log/filter handlers against oversized historical range requests.
2. Supported claim: the change improves availability/resource-control behavior at RPC boundaries.
3. Not supported: a confirmed exploitable denial-of-service vulnerability existed in all affected versions.
4. Not supported: confidentiality, integrity, consensus, or state-corruption impact.
