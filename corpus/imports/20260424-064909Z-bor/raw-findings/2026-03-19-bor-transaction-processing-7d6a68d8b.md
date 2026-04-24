---
case_id: case_20260319_7d6a68d8b
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: resource-exhaustion
source_quality: medium
date: 2026-03-19
source_refs:
  - git:7d6a68d8b3c321b76c32aa5c76af884b6f006d13
  - "eth/filters/api.go:58"
  - "eth/filters/bor_api.go:40"
  - "eth/filters/api.go:524"
  - "eth/filters/api.go:609"
impact_type:
  - availability-impact
confidence: medium
tags:
  - blockchain-core
  - rpc
  - filters
  - resource-exhaustion
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence shows added range-limit enforcement and block-number normalization in `eth/filters` RPC paths, which is consistent with resource-control hardening. But the provided hunks do not establish that a concrete vulnerability previously existed, how severe it was, or whether earlier code lacked other effective protections. This is better treated as security-relevant but unproven from the evidence here.

## Observed Patch Facts

1. In `eth/filters/api.go`, the patch replaces `// filter is a helper struct that holds meta information over the filter type` with `// resolveBlockNumForRangeCheck converts a raw block number (which may be a negative`.

2. In `eth/filters/bor_api.go`, the patch replaces `// Construct the range filter` with `if begin > 0 && end > 0 && begin > end {`.

3. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

4. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

## Project Context

The changed code sits primarily in `eth/filters`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/filters/filter_system_test.go`, `eth/filters/filter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/filters/filter_system_test.go`, `eth/filters/filter.go`. The strongest project-level identifiers around this patch are `head`, `begin`, `filter`, and `crit`.

## Before/After Behavior

Before the patch, the shown `GetLogs`, `GetFilterLogs`, and Bor-specific `GetBorBlockLogs` snippets proceeded from block-range parsing to range-filter construction without a visible `checkBlockRangeLimit(...)` call at those points. After the patch, each path fetches the current head and calls `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` before constructing the range filter. The patch also adds `resolveBlockNumForRangeCheck` so symbolic negative RPC block numbers can be mapped to concrete heights for the guard's arithmetic while preserving the original values for actual filter execution.

# Root Cause

The visible issue is inconsistent or previously missing range-budget enforcement on some RPC log/filter entry points, plus the need to normalize symbolic block numbers for the guard logic. The commit message suggests config pass-through was also involved, but that part is not directly shown in the provided hunks.

## Walkthrough

1. `eth/filters/api.go` adds `resolveBlockNumForRangeCheck`, with comments stating it exists for the range-limit guard and describing how symbolic block numbers are converted for arithmetic.

2. In `GetLogs`, the patched code reads the current head and calls `checkBlockRangeLimit(...)` before `NewRangeFilter(...)` is created.

3. In `GetFilterLogs`, the stored-filter replay path now performs the same head lookup and range-limit check before constructing a range filter.

4. In `eth/filters/bor_api.go`, `GetBorBlockLogs` now adds an explicit positive `begin > end` check and then applies `checkBlockRangeLimit(...)` before creating the Bor range filter.

5. The changed-file list and commit message indicate CLI/config plumbing for `--rpc.rangelimit`, but the supplied evidence does not show those plumbing diffs directly.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/filters/api.go | 52 | Normalizes symbolic RPC block numbers for safe range-limit enforcement. |
| eth/filters/api.go | 475 | Main `GetLogs` RPC path now enforces configured block-range limits before creating a range filter. |
| eth/filters/api.go | 577 | Stored filter replay path (`GetFilterLogs`) now applies the same block-range limit check. |
| eth/filters/bor_api.go | 19 | Bor-specific block log query path now validates range ordering and range limits before filter construction. |

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

Add explicit resource-budget validation at each RPC entry point before expensive filter construction, and normalize symbolic user inputs when the guard logic requires concrete numeric ranges.

## How It Was Fixed

The patch inserts `checkBlockRangeLimit(..., api.sys.cfg.RangeLimit)` into the main log query path, the stored-filter replay path, and the Bor-specific log path before range-filter construction. It also introduces a helper to translate symbolic block numbers into concrete heights only for the guard's calculations. Commit metadata points to corresponding `--rpc.rangelimit` configuration pass-through work, but that wiring is not directly evidenced in the provided hunks.

# Why It Matters

1. Very large log-range queries can be rejected earlier on the visible RPC paths.

2. The same range-budget rule is applied more consistently across multiple filter entry points.

3. Symbolic block-number sentinels are handled explicitly for range-check arithmetic.

4. The evidence supports operational hardening against excessive work more than a proven exploitable vulnerability.

# Evidence Notes

Direct evidence is limited to `eth/filters/api.go` and `eth/filters/bor_api.go`, where new `checkBlockRangeLimit(...)` calls and the `resolveBlockNumForRangeCheck` helper were added. The changed-file list and commit subject mention `--rpc.rangelimit` and config pass-through, but those details are not shown in the supplied code hunks. No provided evidence demonstrates a specific exploit, impact on confidentiality or integrity, or absence of other preexisting protections elsewhere in the call stack. Protocol security invariant: RPC log/filter endpoints should enforce the configured block-range budget before constructing range filters, including when callers use symbolic block numbers such as "latest" or "earliest". Verification notes: The patch does not prove a demonstrated exploit, only that unbounded or misconfigured range queries were a concern. It does not show confidentiality or integrity impact; the visible issue is excessive-query control on RPC paths. It does not prove every prior deployment was vulnerable, because part of the change is config/flag pass-through correctness. It does not establish chain-consensus risk or code execution; the evident risk is request-level resource consumption. The visible diff shows new range-limit checks at three RPC/filter call sites. The visible diff does not show the implementation of `checkBlockRangeLimit` or whether equivalent checks existed deeper in earlier code. The visible diff does not directly prove exploitability, severity, or real-world security impact. Config/flag pass-through is suggested by metadata and changed files, not by the supplied hunks themselves. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `availability-impact`
Final confidence: `medium`
Final tags: `blockchain-core, rpc, filters, resource-exhaustion, security-hardening`

The patch clearly adds and broadens range-limit enforcement on externally reachable RPC log/filter paths and introduces normalization specifically so that the guard applies correctly to symbolic block numbers. That is security-relevant resource-control hardening against expensive queries. However, the supplied hunks do not prove a previously exploitable vulnerability, show the old guard implementation, or establish concrete remote DoS impact, so this should be retained as hardening rather than a confirmed security fix.

## Security Evidence

1. `GetLogs`, `GetFilterLogs`, and `GetBorBlockLogs` now call `checkBlockRangeLimit(...)` before constructing range filters.
2. The new helper `resolveBlockNumForRangeCheck` exists specifically to make range-limit arithmetic work for symbolic RPC block numbers.
3. The commit metadata and touched config/CLI files indicate the range limit was being plumbed through and enforced consistently.
4. The affected code sits on RPC/filter query paths where unbounded ranges can drive excess work.

## Missing Evidence

1. No provided hunk shows the implementation or prior absence of `checkBlockRangeLimit` deeper in the stack.
2. No exploit, benchmark, incident, or severity evidence shows that prior behavior caused a real remotely triggerable DoS.
3. No evidence shows whether the issue depended on misconfiguration versus a universally exposed default weakness.

## Claim Boundaries

1. Supports only RPC/query resource-control hardening, not confidentiality, integrity, or code-execution claims.
2. Does not prove that all prior versions were vulnerable in practice.
3. Does not support a strong `remote-dos` claim from patch evidence alone; only general availability-risk reduction is shown.
