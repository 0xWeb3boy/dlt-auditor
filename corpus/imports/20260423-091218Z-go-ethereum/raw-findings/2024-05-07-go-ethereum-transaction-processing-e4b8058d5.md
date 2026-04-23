---
case_id: case_20240507_e4b8058d5
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2024-05-07
source_refs:
  - git:e4b8058d5a5832cdebdac7da385cf6d829c0d433
  - "eth/gasprice/feehistory.go:242"
  - "eth/gasprice/feehistory.go:45"
bug_class: unbounded-query-parameter
impact_type:
  - availability
tags:
  - blockchain-core
  - rpc
  - resource-control
  - fee-history
  - dos-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a maximum cardinality check for the rewardPercentiles argument in Oracle.FeeHistory. Requests with more than 100 percentiles now fail early with an errInvalidPercentile-derived error. This is supported as DDoS/resource-control hardening, mainly by the explicit commit message and the added query bound, but the evidence does not prove a concrete exploit, crash, or quantified amplification.

## Observed Patch Facts

1. In `eth/gasprice/feehistory.go`, the patch adds `if len(rewardPercentiles) > maxQueryLimit {`.

2. In `eth/gasprice/feehistory.go`, the patch adds `maxQueryLimit = 100`.

## Project Context

The changed code sits primarily in `eth/gasprice`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/gasprice/feehistory_test.go`, `eth/gasprice/gasprice.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/gasprice/gasprice.go`, `eth/gasprice/gasprice_test.go`. The strongest project-level identifiers around this patch are `maxFeeHistory`, `maxQueryLimit`, `blocks`, and `history`.

## Before/After Behavior

Before the change, the visible FeeHistory logic bounded the requested block count through maxHeaderHistory or maxBlockHistory, but showed no equivalent bound on rewardPercentiles length. After the change, maxQueryLimit is defined as 100 and FeeHistory rejects calls where len(rewardPercentiles) exceeds that limit before continuing to block-history processing.

# Root Cause

The FeeHistory path lacked an early cardinality limit for the rewardPercentiles input, leaving one caller-supplied query dimension unchecked while other dimensions such as block history length were already bounded.

## Walkthrough

1. Oracle.FeeHistory receives blocks, unresolvedLastBlock, and rewardPercentiles as inputs.

2. The function selects maxFeeHistory from oracle.maxHeaderHistory or oracle.maxBlockHistory depending on whether rewardPercentiles is empty.

3. Before the patch, the provided snippet shows the next visible resource-control check only truncating blocks when blocks exceeds maxFeeHistory.

4. The patch adds maxQueryLimit = 100 near the existing maxBlockFetchers constant.

5. The patch adds an early len(rewardPercentiles) > maxQueryLimit check.

6. Over-limit requests now return common.Big0, nil result values, and an error wrapping errInvalidPercentile instead of proceeding further.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/gasprice/feehistory.go | 45 | Defines maxQueryLimit as the upper bound for reward percentile query cardinality. |
| eth/gasprice/feehistory.go | 242 | Validates len(rewardPercentiles) in Oracle.FeeHistory and returns errInvalidPercentile when the query exceeds the limit. |

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

Add an explicit upper bound for a caller-controlled query parameter and reject over-limit requests before expensive downstream processing.

## How It Was Fixed

The fix defines maxQueryLimit = 100 and inserts a guard in Oracle.FeeHistory that returns an errInvalidPercentile-derived error when rewardPercentiles contains more than 100 entries.

# Why It Matters

1. Bounds a caller-controlled FeeHistory query dimension.

2. Complements existing block-history limits.

3. Turns excessive percentile cardinality into a normal validation error.

4. Supports DDoS hardening without claiming a proven crash or consensus impact.

# Evidence Notes

Primary evidence is limited to eth/gasprice/feehistory.go. The changed lines add maxQueryLimit = 100 and a len(rewardPercentiles) guard in Oracle.FeeHistory. The commit message explicitly frames the change as a DDoS defense. The supplied evidence does not prove remote reachability, crash behavior, transaction-processing impact, consensus impact, state corruption, or quantified CPU/memory amplification. Protocol security invariant: The FeeHistory/gasprice oracle path should bound caller-controlled query dimensions so a request cannot force unbounded fee-history work or response construction. The supplied patch establishes a limit on rewardPercentiles length; it does not establish a consensus, transaction-validation, or crash-safety invariant. Verification notes: The patch does not prove remote crash or process termination. The patch does not show transaction decoding, mempool, or block-processing behavior. The patch does not prove consensus impact or chain state corruption. The patch does not quantify CPU, memory, or bandwidth amplification before the limit. The patch shows request-size/resource hardening, not authentication or authorization enforcement. Confirmed from supplied diff that only rewardPercentiles length is newly bounded. Confirmed the heuristic transaction-processing and panic claims are unsupported by the provided evidence. No supplied test evidence demonstrates exploitability or resource-amplification magnitude. Classification is security hardening rather than confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unbounded-query-parameter`
Final impact type: `availability`
Final tags: `blockchain-core, rpc, resource-control, fee-history, dos-hardening`

The supplied patch and commit metadata support retaining this as security hardening: FeeHistory gains an explicit upper bound on the caller-controlled rewardPercentiles array, and the commit message frames the change as DDoS defense. The evidence does not prove a concrete exploit, crash, consensus failure, or quantified amplification, so it should not be promoted to a confirmed vulnerability fix.

## Security Evidence

1. Commit subject/body explicitly says the query limit was added to defend against DDoS.
2. FeeHistory now rejects len(rewardPercentiles) greater than maxQueryLimit before further processing.
3. The new constant maxQueryLimit = 100 bounds a previously unbounded caller-supplied query dimension.
4. The changed logic is resource-control validation rather than unrelated maintenance.

## Missing Evidence

1. No proof of remote reachability is shown in the supplied evidence.
2. No exploit, crash, timeout, or memory/CPU amplification measurement is provided.
3. No test evidence demonstrates denial-of-service behavior before the patch.
4. No evidence supports consensus impact, transaction validation impact, or state corruption.

## Claim Boundaries

1. Classify as security-hardening, not a proven security-fix.
2. Limit claims to FeeHistory rewardPercentiles cardinality control.
3. Do not claim consensus, chain-state, authentication, or authorization impact.
4. Do not claim a concrete exploitable DDoS beyond the commit message and added resource bound.
