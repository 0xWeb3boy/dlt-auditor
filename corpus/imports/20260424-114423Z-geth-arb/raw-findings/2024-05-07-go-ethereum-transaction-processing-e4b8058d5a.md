---
case_id: case_20240507_e4b8058d5a
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: resource-exhaustion
confidence: medium
source_quality: medium
date: 2024-05-07
source_refs:
  - git:e4b8058d5a5832cdebdac7da385cf6d829c0d433
  - "eth/gasprice/feehistory.go:242"
  - "eth/gasprice/feehistory.go:45"
impact_type:
  - dos
  - resource-exhaustion
tags:
  - blockchain-core
  - rpc
  - fee-history
  - resource-exhaustion
  - dos-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens go-ethereum's eth/gasprice FeeHistory path by adding a maximum length for caller-supplied rewardPercentiles. It defines maxQueryLimit = 100 and rejects requests with more than 100 reward percentiles before continuing into fee history processing. The evidence supports resource-control hardening consistent with the commit message's DDoS wording, but does not prove a concrete exploit path or measured denial-of-service impact.

## Observed Patch Facts

1. In `eth/gasprice/feehistory.go`, the patch adds `if len(rewardPercentiles) > maxQueryLimit {`.

2. In `eth/gasprice/feehistory.go`, the patch adds `maxQueryLimit = 100`.

## Project Context

The changed code sits primarily in `eth/gasprice`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/gasprice/feehistory_test.go`, `eth/gasprice/gasprice.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/gasprice/gasprice.go`, `eth/gasprice/gasprice_test.go`. The strongest project-level identifiers around this patch are `maxFeeHistory`, `maxQueryLimit`, `blocks`, and `history`.

## Before/After Behavior

Before the change, the provided FeeHistory snippet bounded the requested block history length through maxHeaderHistory or maxBlockHistory, but showed no equivalent limit on len(rewardPercentiles). After the change, FeeHistory returns an errInvalidPercentile-derived error when len(rewardPercentiles) exceeds 100, while the existing block-count truncation behavior remains unchanged.

# Root Cause

The visible pre-patch code constrained the number of blocks but did not constrain the number of reward percentiles supplied to FeeHistory. That left one caller-controlled query dimension without an explicit maximum before downstream processing.

## Walkthrough

1. A caller invokes Oracle.FeeHistory with blocks, unresolvedLastBlock, and rewardPercentiles.

2. FeeHistory selects maxFeeHistory from oracle.maxHeaderHistory, or oracle.maxBlockHistory when rewardPercentiles is non-empty.

3. Before the patch, the next visible resource-control check only sanitized blocks when it exceeded maxFeeHistory.

4. The patch adds maxQueryLimit = 100 to the FeeHistory constants.

5. The patch adds a guard that rejects len(rewardPercentiles) greater than maxQueryLimit.

6. Oversized rewardPercentiles requests now return nil result data and an error wrapping errInvalidPercentile.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/gasprice/feehistory.go | 45 | defines maxQueryLimit constant used to cap reward percentile query width |
| eth/gasprice/feehistory.go | 242 | validates caller-supplied rewardPercentiles length in Oracle.FeeHistory before history processing |

## Code Snippets

## Snippet 1

Context: `eth/gasprice/feehistory.go:242` (changes bounds, limits, or capacity handling)

Before
```go
maxFeeHistory = oracle.maxBlockHistory
	}
	if blocks > maxFeeHistory {
		log.Warn("Sanitizing fee history length", "requested", blocks, "truncated", maxFeeHistory)
```
After
```go
maxFeeHistory = oracle.maxBlockHistory
	}
	if len(rewardPercentiles) > maxQueryLimit {
		return common.Big0, nil, nil, nil, nil, nil, fmt.Errorf("%w: over the query limit %d", errInvalidPercentile, maxQueryLimit)
	}
	if blocks > maxFeeHistory {
		log.Warn("Sanitizing fee history length", "requested", blocks, "truncated", maxFeeHistory)
```

## Snippet 2

Context: `eth/gasprice/feehistory.go:45` (changes a sensitive control or state-update path)

Before
```go
// for the fee history calculation (mostly relevant for LES).
	maxBlockFetchers = 4
)
```
After
```go
// for the fee history calculation (mostly relevant for LES).
	maxBlockFetchers = 4
	maxQueryLimit    = 100
)
```

# Fix Pattern

Add a named upper bound for a caller-controlled query dimension and fail fast with a normal error before expensive processing continues.

## How It Was Fixed

The fix introduced maxQueryLimit = 100 and added a check in Oracle.FeeHistory that returns common.Big0, nil result slices, and fmt.Errorf wrapping errInvalidPercentile when len(rewardPercentiles) exceeds that limit.

# Why It Matters

1. Bounds a caller-controlled FeeHistory input dimension.

2. Reduces potential excessive reward percentile processing from a single request.

3. Keeps block-count limiting separate from reward-percentile limiting.

4. Does not evidence crash, panic, consensus failure, transaction decoding, authorization, or memory corruption issues.

# Evidence Notes

Evidence is limited to eth/gasprice/feehistory.go. The patch adds maxQueryLimit = 100 near maxBlockFetchers and adds len(rewardPercentiles) > maxQueryLimit validation inside Oracle.FeeHistory. The commit message explicitly describes a DDoS defense. The code evidence supports resource-exhaustion hardening, but not a confirmed vulnerability with demonstrated exploitability. Protocol security invariant: FeeHistory should bound caller-controlled query dimensions before doing fee history reward processing so a single request cannot request an excessive number of reward percentile calculations. Verification notes: No concrete exploit path or measured amplification is shown by the patch alone. No crash, panic, memory corruption, or consensus failure is evidenced. No authentication, authorization, or transaction-processing invariant is changed. The patch proves a bounded-query hardening change, not necessarily an independently exploitable vulnerability. No concrete exploit path is shown in the provided evidence. No performance measurements or amplification details are provided. No tests are shown for the new limit in the provided input. The heuristic transaction-processing and panic claims are unsupported and removed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `dos, resource-exhaustion`
Final tags: `blockchain-core, rpc, fee-history, resource-exhaustion, dos-hardening`

The supplied evidence supports retaining this as security hardening. The patch adds a fixed upper bound on caller-supplied rewardPercentiles in FeeHistory and rejects oversized inputs, and the commit message explicitly frames the change as DDoS defense. The code does not prove a concrete exploit path, measured amplification, or actual service outage, so it should not be promoted to a confirmed security-fix case.

## Security Evidence

1. Commit subject/body explicitly says the FeeHistory query limit was added to defend against DDoS.
2. Patch introduces maxQueryLimit = 100.
3. FeeHistory now rejects len(rewardPercentiles) greater than maxQueryLimit before continuing.
4. The changed input is caller-controlled function input on a FeeHistory/RPC-shaped code path.

## Missing Evidence

1. No demonstrated exploit path is shown.
2. No performance or amplification measurements are provided.
3. No evidence shows unauthenticated remote reachability from the patch alone.
4. No tests or incident details are included.

## Claim Boundaries

1. Classify as resource-exhaustion/DOS hardening, not a proven exploitable vulnerability.
2. Do not claim consensus impact from the supplied evidence.
3. Do not claim crash, panic, memory corruption, authorization bypass, or transaction validation impact.
4. Remote DOS is plausible from commit wording and RPC-shaped context, but the code evidence alone only proves bounded-query hardening.
