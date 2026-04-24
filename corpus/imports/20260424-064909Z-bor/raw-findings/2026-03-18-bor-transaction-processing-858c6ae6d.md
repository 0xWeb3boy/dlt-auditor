---
case_id: case_20260318_858c6ae6d
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
  - git:858c6ae6d5fb4fbcccf7ff3c609ed07d464f7d18
  - "eth/filters/api.go:58"
  - "eth/filters/bor_api.go:40"
  - "eth/filters/api.go:524"
  - "eth/filters/api.go:609"
bug_class: missing-resource-limit-enforcement
impact_type:
  - availability
  - resource-exhaustion
confidence: medium
tags:
  - rpc
  - resource-control
  - query-range-limit
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a resource-control and correctness change in the RPC log-filter subsystem: range-based log queries now check a configured block-range limit before building filters, and symbolic block numbers are normalized for that check. The supplied hunks do not establish a concrete vulnerability or demonstrated exploit path, so this should be treated as unclear rather than confirmed security work.

## Observed Patch Facts

1. In `eth/filters/api.go`, the patch replaces `// filter is a helper struct that holds meta information over the filter type` with `// resolveBlockNumForRangeCheck converts a raw block number (which may be a negative`.

2. In `eth/filters/bor_api.go`, the patch replaces `// Construct the range filter` with `if begin > 0 && end > 0 && begin > end {`.

3. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

4. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

## Project Context

The changed code sits primarily in `eth/filters`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/filters/filter_system_test.go`, `eth/filters/filter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/filters/filter_system_test.go`, `eth/filters/filter.go`. The strongest project-level identifiers around this patch are `head`, `begin`, `filter`, and `crit`.

## Before/After Behavior

Before the patch, the shown `GetLogs`, `GetFilterLogs`, and `GetBorBlockLogs` paths derived `begin` and `end` and then proceeded to construct range filters without any visible `checkBlockRangeLimit(...)` call in the provided snippets. After the patch, each shown range path fetches the current head and invokes `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` before constructing the filter, and the code adds `resolveBlockNumForRangeCheck` to map symbolic negative block numbers to concrete values for that validation logic.

# Root Cause

The visible issue is inconsistent or missing enforcement of a configured block-range limit in several RPC log-filter entry points. The commit subject also mentions config pass-through, but the provided evidence does not show that wiring bug directly.

## Walkthrough

1. `eth/filters/api.go` adds `resolveBlockNumForRangeCheck` and documents how negative symbolic block numbers are interpreted for range-limit arithmetic.

2. In `GetLogs`, the code now reads the current head and calls `checkBlockRangeLimit(...)` before `NewRangeFilter(...)`.

3. In `GetFilterLogs`, the replay path for stored criteria now performs the same range-limit check before rebuilding the range filter.

4. In `GetBorBlockLogs`, the code now rejects inverted positive ranges and also applies `checkBlockRangeLimit(...)` before constructing the Bor range filter.

5. The repeated check placement shows a consistency fix across multiple visible RPC range-query paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/filters/api.go | 58 | Normalize symbolic RPC block numbers into concrete heights for range-limit enforcement without changing actual filter semantics |
| eth/filters/api.go | 475 | Main `GetLogs` range-query path now enforces the configured block-range limit before creating a range filter |
| eth/filters/api.go | 577 | `GetFilterLogs` replay path now re-applies the configured block-range limit to stored filter criteria |
| eth/filters/bor_api.go | 19 | Bor-specific block-log query path now rejects inverted ranges and enforces the configured block-range limit |

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

Add centralized precondition checks at each range-query entry point so configured resource limits are enforced before expensive filter construction, with explicit normalization of symbolic inputs for validation.

## How It Was Fixed

The patch inserts `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` into the visible range-query paths and introduces helper logic to convert symbolic block selectors into concrete heights for that check. It also adds an explicit invalid-range rejection in the Bor-specific path. CLI/config files were touched, but their exact effect is not shown in the supplied evidence.

# Why It Matters

1. Constrains oversized range queries on the shown RPC paths.

2. Makes direct queries and saved-filter replay follow the same limit check.

3. Prevents symbolic block selectors from confusing range-limit arithmetic.

4. Improves consistency in a resource-sensitive code path.

# Evidence Notes

Strongest support comes from the added `checkBlockRangeLimit(...)` calls in `eth/filters/api.go` and `eth/filters/bor_api.go`, plus the new `resolveBlockNumForRangeCheck` helper comments. The commit subject suggests a flag/config pass-through fix, but those code hunks were not provided. The evidence supports a range-limit enforcement change; it does not by itself prove externally reachable abuse, impact severity, or a specific security exploit. Protocol security invariant: Range-based RPC log queries should consistently enforce the configured maximum block span across direct queries, saved-filter replay, and Bor-specific paths. Symbolic block selectors must be converted to concrete heights for range-limit arithmetic without changing actual filter semantics. Verification notes: The patch does not prove the RPC endpoint was exposed to untrusted callers in all deployments. The provided hunks do not demonstrate a measured denial-of-service exploit, only that oversized range queries are now constrained. The evidence does not show confidentiality, integrity, or consensus-safety impact. The exact config pass-through bug is implied by the commit subject and touched files, but its pre-patch wiring is not fully shown in the provided hunks. No test diff was provided showing a reproduced bypass or exploit. No evidence here shows whether affected RPC methods were exposed to untrusted users in practice. The supplied hunks support a hardening/correctness interpretation more directly than a confirmed vulnerability claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-limit-enforcement`
Final impact type: `availability, resource-exhaustion`
Final confidence: `medium`
Final tags: `rpc, resource-control, query-range-limit, availability-hardening`

The patch evidence supports a security-hardening interpretation. Multiple RPC log-query entry points now enforce a configured block-range limit before constructing range filters, and symbolic block selectors are normalized specifically for that guard. That is a clear tightening of resource-control behavior on externally callable query paths, which is security-relevant because it reduces the risk of expensive oversized requests. However, the provided hunks do not prove a concrete exploitable denial-of-service issue, real-world exposure, or measured impact, so this should not be elevated to a confirmed security fix.

## Security Evidence

1. `GetLogs` now calls `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` before constructing a range filter.
2. `GetFilterLogs` adds the same range-limit enforcement for replayed/saved filter criteria.
3. `GetBorBlockLogs` now rejects inverted positive ranges and enforces the configured range limit before building the Bor filter.
4. `resolveBlockNumForRangeCheck` was added to normalize symbolic negative block numbers for range-limit arithmetic, showing intentional guard hardening rather than incidental refactoring.
5. The commit subject and body explicitly mention adding an `--rpc.rangelimit` flag and applying more range checks.

## Missing Evidence

1. No supplied hunk shows a demonstrated exploit, benchmark, or incident tied to oversized RPC range queries.
2. The evidence does not show whether these RPC methods were exposed to untrusted callers in affected deployments.
3. The config pass-through bug referenced in the commit subject is not fully shown in the provided patch evidence.
4. No test evidence is included proving a prior bypass of the configured range limit.

## Claim Boundaries

1. Supported claim: the commit hardens RPC log-filter paths by enforcing configured block-range limits more consistently.
2. Supported claim: the change is security-relevant because it constrains potentially expensive requests on a resource-sensitive path.
3. Not supported: a confirmed exploitable vulnerability existed in all affected versions or deployments.
4. Not supported: confidentiality, integrity, privilege-escalation, or consensus-safety impact.
5. Not supported: severity beyond conservative availability/resource-exhaustion hardening.
