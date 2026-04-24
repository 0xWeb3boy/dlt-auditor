---
case_id: case_20240507_e4b8058d5
project: bor
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
  - denial-of-service
tags:
  - blockchain-core
  - rpc
  - resource-exhaustion
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely hardens the FeeHistory path against denial-of-service style resource abuse by adding a fixed limit on the length of the caller-supplied `rewardPercentiles` array.

## Observed Patch Facts

1. In `eth/gasprice/feehistory.go`, the patch adds `if len(rewardPercentiles) > maxQueryLimit {`.

2. In `eth/gasprice/feehistory.go`, the patch adds `maxQueryLimit = 100`.

## Project Context

The changed code sits primarily in `eth/gasprice`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/gasprice/feehistory_test.go`, `eth/gasprice/gasprice.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/gasprice/gasprice.go`, `eth/gasprice/gasprice_test.go`. The strongest project-level identifiers around this patch are `maxFeeHistory`, `maxQueryLimit`, `blocks`, and `history`.

## Before/After Behavior

Before the patch, the shown `FeeHistory` code limited `blocks` via `maxFeeHistory`, but the provided pre-patch snippet shows no comparable bound on `len(rewardPercentiles)`. After the patch, requests with more than `100` reward percentiles are rejected early with an `errInvalidPercentile`-wrapped error, while the existing block-count truncation remains in place.

# Root Cause

A request-cost dimension was left unchecked: `FeeHistory` accepted an unbounded number of reward percentiles in the shown pre-patch code, even though block count was already bounded.

## Walkthrough

1. `FeeHistory` accepts `rewardPercentiles []float64` as an input parameter.

2. The pre-patch excerpt shows logic to cap `blocks` but no shown check on `len(rewardPercentiles)`.

3. The patch adds `maxQueryLimit = 100` in the same file.

4. The patch adds an early branch that returns an error when `len(rewardPercentiles) > maxQueryLimit`.

5. That change converts oversized percentile lists from accepted input into rejected input before further fee-history processing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/gasprice/feehistory.go | 236 | Oracle FeeHistory request handling and input validation for externally supplied query parameters |
| eth/gasprice/feehistory.go | 242 | New rejection path when `rewardPercentiles` exceeds the configured query bound |
| eth/gasprice/feehistory.go | 45 | Definition of the global percentile-count cap used to constrain request cost |

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

Add an explicit upper bound for an unbounded caller-controlled input dimension and fail fast before downstream processing.

## How It Was Fixed

`eth/gasprice/feehistory.go` now defines `maxQueryLimit = 100` and checks `len(rewardPercentiles)` near the start of `Oracle.FeeHistory`. If the array is too large, the function returns immediately with an error instead of continuing.

# Why It Matters

1. It closes a visible gap where one query dimension was not bounded.

2. It reduces the chance that a single FeeHistory request can force excessive work through a very large percentile list.

3. It complements the existing block-history limit rather than changing fee calculation semantics.

4. The evidence supports availability hardening, not confidentiality, integrity, or consensus impact.

# Evidence Notes

The code evidence directly supports a new resource-control check in `FeeHistory`: addition of `maxQueryLimit = 100` and an early rejection when `len(rewardPercentiles)` exceeds that limit. The commit message explicitly says the change is to defend against a DDoS attack, which is consistent with the added bound. The evidence does not prove exploitability details such as remote reachability in every deployment, exact resource type affected, or a previously demonstrated crash. Protocol security invariant: FeeHistory processing should bound caller-supplied query dimensions before doing fee-history work. In particular, the number of requested reward percentiles must be capped so one request cannot expand work arbitrarily along that axis. Verification notes: The patch does not prove a previously exploitable crash; it shows bounded rejection of oversized queries. The patch does not establish whether the attack was remotely reachable without authentication in every deployment. The diff does not quantify whether the prior impact was CPU exhaustion, memory pressure, latency amplification, or all three. No confidentiality, integrity, or consensus-safety issue is shown by this change. The patch evidence is limited to this FeeHistory query dimension and does not prove broader gasprice subsystem flaws. Verified from the diff that only `eth/gasprice/feehistory.go` changed. Verified that the new behavior is an added length check on `rewardPercentiles`. Verified that existing `blocks` limiting logic remains after the new check. Did not see evidence of confidentiality, integrity, or consensus-safety impact. Did not see evidence strong enough to upgrade from likely hardening to confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `denial-of-service`
Final tags: `blockchain-core, rpc, resource-exhaustion, availability`

The patch adds a fixed upper bound on a caller-controlled `rewardPercentiles` input in `FeeHistory` and rejects oversized requests before further processing. That is direct evidence of availability hardening against request-amplified work, and the commit message explicitly frames it as DDoS defense. However, the diff alone does not prove concrete exploitability, remote unauthenticated reachability in all deployments, or a demonstrated pre-fix outage, so this is best retained as security hardening rather than a confirmed vulnerability fix.

## Security Evidence

1. `FeeHistory` now rejects `rewardPercentiles` arrays longer than `maxQueryLimit` before continuing.
2. The new constant `maxQueryLimit = 100` introduces an explicit resource-control bound on user-supplied input.
3. The function already bounded `blocks`; this patch closes another request-cost dimension that was previously unchecked in the shown code.
4. The commit subject/body explicitly says the change is to defend against a DDoS attack.

## Missing Evidence

1. No proof of a previously exploitable crash, hang, or measurable resource exhaustion from the old behavior.
2. No evidence that the affected path is remotely reachable without authentication in every deployment.
3. No quantification of the pre-fix cost impact on CPU, memory, or latency.
4. No test or benchmark evidence showing the old path could be abused at scale.

## Claim Boundaries

1. Supported claim: this patch hardens an RPC-like fee history path by capping a caller-controlled query dimension.
2. Supported claim: the change reduces risk of oversized requests causing excessive work.
3. Not supported: a confirmed exploitable remote DoS vulnerability across all configurations.
4. Not supported: confidentiality, integrity, or consensus impact.
