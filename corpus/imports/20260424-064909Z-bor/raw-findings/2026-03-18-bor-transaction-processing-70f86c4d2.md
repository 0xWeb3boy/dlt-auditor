---
case_id: case_20260318_70f86c4d2
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
  - git:70f86c4d23c13c1705be47aa6fcc65528d8b45dd
  - "eth/filters/api.go:58"
  - "eth/filters/bor_api.go:40"
  - "eth/filters/api.go:524"
  - "eth/filters/api.go:609"
bug_class: insufficient-rpc-range-limit-enforcement
impact_type:
  - availability
confidence: medium
tags:
  - rpc
  - resource-control
  - availability-hardening
  - blockchain-core
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch shows previously missing or incomplete range-limit enforcement in RPC log-filter paths, plus normalization of symbolic block numbers for that check. That is resource-control relevant, but the provided evidence does not establish an actual exploitable vulnerability rather than a correctness or hardening fix.

## Observed Patch Facts

1. In `eth/filters/api.go`, the patch replaces `// filter is a helper struct that holds meta information over the filter type` with `// resolveBlockNumForRangeCheck converts a raw block number (which may be a negative`.

2. In `eth/filters/bor_api.go`, the patch replaces `// Construct the range filter` with `if begin > 0 && end > 0 && begin > end {`.

3. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

4. In `eth/filters/api.go`, the patch adds `head := api.sys.backend.CurrentHeader().Number.Uint64()`.

## Project Context

The changed code sits primarily in `eth/filters`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/filters/filter_system_test.go`, `eth/filters/filter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/filters/filter_system_test.go`, `eth/filters/filter.go`. The strongest project-level identifiers around this patch are `head`, `begin`, `filter`, and `crit`.

## Before/After Behavior

Before the patch, the shown `GetLogs`, `GetFilterLogs`, and Bor range-log paths constructed range filters without any visible `checkBlockRangeLimit(...)` call, and the Bor path excerpt also lacked the shown positive-range reversal check. After the patch, those paths fetch the current head, call `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` before constructing range filters, and `api.go` adds `resolveBlockNumForRangeCheck` so symbolic negative selectors can be converted for validation without changing filter semantics.

# Root Cause

Range-limit enforcement was not consistently applied in the RPC filter code paths handling block-range log queries, and symbolic block selectors needed explicit normalization for that validation logic.

## Walkthrough

1. `eth/filters/api.go` adds `resolveBlockNumForRangeCheck` with comments describing how symbolic negative block numbers are mapped for range arithmetic.

2. In `GetLogs`, the code now obtains `head` and calls `checkBlockRangeLimit(...)` before `NewRangeFilter(...)`.

3. In `GetFilterLogs`, the code now performs the same `head` lookup and `checkBlockRangeLimit(...)` before constructing the range filter.

4. In `GetBorBlockLogs`, the patch adds both a positive `begin > end` rejection and a `checkBlockRangeLimit(...)` call before `NewBorBlockLogsRangeFilter(...)`.

5. The commit title also mentions `--rpc.rangelimit` and filter config pass-through, which is consistent with enforcement/config wiring rather than proof of a concrete vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/filters/api.go | 58 | normalizes symbolic block numbers for range-limit enforcement without changing actual filter semantics |
| eth/filters/api.go | 524 | applies block-range limit check in `GetLogs` before constructing a range filter |
| eth/filters/api.go | 609 | applies block-range limit check when retrieving logs from an existing filter id |
| eth/filters/bor_api.go | 40 | adds invalid-range rejection and range-limit enforcement for Bor block log queries |

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

Add centralized pre-execution range validation to each range-query entry point and normalize symbolic inputs only for the validation step.

## How It Was Fixed

The code now computes the current head height, checks the requested span against `api.sys.cfg.RangeLimit`, and returns an error before constructing range filters when the request is invalid or exceeds the configured bound. It also adds helper logic so symbolic selectors like `earliest` and `latest` can participate in the limit check correctly.

# Why It Matters

1. These RPC paths can drive historical log-query work, so span checks are operationally important.

2. The patch makes range validation explicit and consistent across multiple entry points.

3. The evidence supports resource-control hardening, but not a confirmed security impact.

# Evidence Notes

The grounded evidence is limited to added calls to `checkBlockRangeLimit(...)`, the new block-number normalization helper, the Bor invalid-range check, and commit metadata mentioning `--rpc.rangelimit` and config pass-through. The provided material does not show the prior implementation of `checkBlockRangeLimit`, the default configuration state, whether exposed deployments were affected, or any demonstrated denial-of-service outcome. That is not enough to confirm a security fix. Protocol security invariant: Range-based RPC log queries should enforce configured block-span limits before constructing range filters, including when clients use symbolic block selectors that must be normalized for limit checking. Verification notes: The patch does not prove a previously exploitable remote DoS, only that expensive ranges were insufficiently constrained. The patch does not show confidentiality, integrity, or authorization impact. The exact default limit value and whether vulnerable deployments exposed these RPC methods are not proven from the provided evidence. The commit also includes config/flag pass-through work, but the provided hunks do not prove a broader protocol flaw beyond missing enforcement of query span limits. Confirmed from the shown hunks that range checks were added in `GetLogs`, `GetFilterLogs`, and `GetBorBlockLogs`. Confirmed that symbolic block-number normalization was added specifically for range checking. Did not see evidence proving exploitability, default exposure, or real-world impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-rpc-range-limit-enforcement`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `rpc, resource-control, availability-hardening, blockchain-core`

The patch clearly tightens security-sensitive resource controls on RPC log-filter endpoints by enforcing a configured block-range limit before constructing expensive range filters and by normalizing symbolic block selectors for that guard. That supports retaining it as a security-hardening case focused on availability protection. The evidence does not, however, prove a concrete exploitable vulnerability, default exposure, or an observed denial-of-service condition, so this should not be labeled a confirmed security fix.

## Security Evidence

1. `checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit)` was added before range-filter construction in `GetLogs`, `GetFilterLogs`, and `GetBorBlockLogs`.
2. A new `resolveBlockNumForRangeCheck` helper maps symbolic negative block selectors to concrete heights specifically for range-limit enforcement.
3. The Bor-specific path now rejects invalid positive ranges and applies the same range-limit check.
4. Commit metadata explicitly references `--rpc.rangelimit` and filter config pass-through, consistent with request-bounding hardening on RPC endpoints.

## Missing Evidence

1. No proof that the old behavior was remotely exploitable in default or common deployments.
2. No advisory, test, or commit text showing an actual denial-of-service incident or demonstrated attack.
3. No evidence here of the prior/default `RangeLimit` configuration or whether affected RPC methods were broadly exposed.

## Claim Boundaries

1. Supported: the commit hardens RPC log-query resource control and closes missing enforcement paths.
2. Supported: the change is relevant to availability protection for potentially expensive range queries.
3. Not supported: a confirmed remotely exploitable security bug existed before this patch.
4. Not supported: any confidentiality, integrity, or authorization impact.
