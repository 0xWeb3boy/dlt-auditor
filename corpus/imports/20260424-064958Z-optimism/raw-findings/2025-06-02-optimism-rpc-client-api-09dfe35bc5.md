---
case_id: case_20250602_09dfe35bc5
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2025-06-02
source_refs:
  - git:09dfe35bc5ebe7e55b6d87d0df8d8c147e4520d2
  - "op-supervisor/supervisor/types/types.go:317"
  - "op-supervisor/supervisor/backend/backend.go:573"
  - "op-supervisor/supervisor/types/types_test.go:347"
  - "op-supervisor/supervisor/backend/depset/links.go:58"
bug_class: access-control-validation
impact_type:
  - policy-bypass-risk
confidence: medium
tags:
  - blockchain-core
  - interop
  - access-list-validation
  - time-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens `op-supervisor` access-list validation, but the provided evidence does not establish a concrete vulnerability. It shows stricter handling of same-timestamp execution, explicit use of executing-chain context with a backward-compatibility fallback when that chain ID is missing, and safer expiry arithmetic.

## Observed Patch Facts

1. In `op-supervisor/supervisor/types/types.go`, the patch replaces `func (ed *ExecutingDescriptor) AccessCheck(expiryWindow uint64, initMsgTimestamp uint...` with `type executingDescriptorMarshaling struct {`.

2. In `op-supervisor/supervisor/backend/backend.go`, the patch replaces `// Register as a dependency` with `// Register initiating side as a dependency`.

3. In `op-supervisor/supervisor/types/types_test.go`, the patch replaces `type execDescrTestCase struct {` with `func TestPayloadHashToLogHash(t *testing.T) {`.

4. In `op-supervisor/supervisor/backend/depset/links.go`, the patch replaces `window := lc.cfg.MessageExpiryWindow()` with `expiresAt := safemath.SaturatingAdd(initTimestamp, lc.cfg.MessageExpiryWindow())`.

## Project Context

The changed code sits primarily in `op-supervisor/supervisor/types`, `op-supervisor/supervisor`, `op-supervisor/supervisor/backend`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `op-supervisor/supervisor/backend/mock.go`, `op-supervisor/supervisor/backend/depset/rollup_config_set.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-supervisor/supervisor/backend/mock.go`, `op-supervisor/supervisor/backend/depset/rollup_config_set.go`. The strongest project-level identifiers around this patch are `Timestamp`, `initMsgTimestamp`, `uint64`, and `expiresAt`.

## Before/After Behavior

Before the patch, `ExecutingDescriptor.AccessCheck` rejected execution earlier than the initiating timestamp but did not explicitly reject the equal-timestamp case. `CheckAccessList` also had to cope with callers that did not provide an executing chain ID, and expiry logic in `links.go` used manual overflow handling. After the patch, same-timestamp execution is explicitly rejected, the executing chain ID is carried or reconstructed with a compatibility fallback, and expiry uses `safemath.SaturatingAdd`.

# Root Cause

The validation path did not fully encode or enforce all of the execution context and edge-case rules needed by the interop access-list check. In particular, same-timestamp execution was not explicitly blocked in `AccessCheck`, callers could omit the executing chain ID, and expiry arithmetic relied on a hand-rolled overflow pattern.

## Walkthrough

1. `CheckAccessList` parses access-list entries and records the initiating side as a dependency.

2. The patch adds logic to derive `execChainID` from `execDescr.ChainID`, with a fallback to the initiating chain when the caller omitted it.

3. `ExecutingDescriptor.AccessCheck` is tightened with an explicit conflict when `ed.Timestamp == initMsgTimestamp`.

4. `links.go` continues enforcing interop and expiry conditions, but switches expiry computation to `safemath.SaturatingAdd`.

5. Tests were added or updated around `ExecutingDescriptor.AccessCheck`, indicating the stricter time behavior is intentional.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-supervisor/supervisor/backend/backend.go | 550 | Main access-list validation flow; parses initiating entries, binds dependencies, and evaluates execution eligibility using executing-chain context. |
| op-supervisor/supervisor/types/types.go | 317 | `ExecutingDescriptor.AccessCheck` enforces strict temporal and expiry constraints for the executing message descriptor. |
| op-supervisor/supervisor/backend/depset/links.go | 32 | Dependency-set link checker that enforces chain membership, interop activation, activation-block exclusion, and expiry-window validity. |

## Code Snippets

## Snippet 1

Context: `op-supervisor/supervisor/types/types.go:317` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (ed *ExecutingDescriptor) AccessCheck(expiryWindow uint64, initMsgTimestamp uint64) error {
	// Check upper-bound invariant, strictly
	// (for access-lists we don't afford to check intra-timestamp dependencies)
	if ed.Timestamp < initMsgTimestamp {
		return fmt.Errorf("message broke timestamp invariant: exec: %d, init: %d, %w",
			ed.Timestamp, initMsgTimestamp, ErrConflict)
```
After
```go
}

type executingDescriptorMarshaling struct {
	ChainID   eth.ChainID    `json:"chainID"`
	Timestamp hexutil.Uint64 `json:"timestamp"`
	Timeout   hexutil.Uint64 `json:"timeout,omitempty"`
```

## Snippet 2

Context: `op-supervisor/supervisor/backend/backend.go:573` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
entries = remaining

		// Register as a dependency
		h.DependOnDerivedTime(acc.Timestamp)

		// Check if message passes time checks
		if err := executingDescriptor.AccessCheck(su.cfgSet.MessageExpiryWindow(), acc.Timestamp); err != nil {
			su.logger.Warn("Access-list time check failed", "err", err)
```
After
```go
entries = remaining

		// Register initiating side as a dependency
		h.DependOnDerivedTime(acc.Timestamp)

		// TODO(#16245): backwards compat: if user does not specify executing chain, then assume the initiating chain ID.
		// This supports op-reth, op-rbuilder, proxyd while they are not updated to provide this chain ID.
		execChainID := execDescr.ChainID
```

## Snippet 3

Context: `op-supervisor/supervisor/types/types_test.go:347` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

type execDescrTestCase struct {
	name             string
	ed               ExecutingDescriptor
	expiryWindow     uint64
	initMsgTimestamp uint64
	errStr           string // empty if no error
```
After
```go
}

func TestPayloadHashToLogHash(t *testing.T) {
	logHash := PayloadHashToLogHash(testMsgHash, testOrigin)
```

## Snippet 4

Context: `op-supervisor/supervisor/backend/depset/links.go:58` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return false
	}
	window := lc.cfg.MessageExpiryWindow()
	expiresAt := initTimestamp + window
	if expiresAt < initTimestamp { // happens upon underflow
		return false
	}
	if expiresAt < execInTimestamp { // expiry check
```
After
```go
return false
	}
	expiresAt := safemath.SaturatingAdd(initTimestamp, lc.cfg.MessageExpiryWindow())
	if expiresAt < execInTimestamp { // expiry check
		return false
```

# Fix Pattern

Tighten admission checks by making required context explicit, rejecting ambiguous edge cases, and replacing manual arithmetic guards with safer helper logic.

## How It Was Fixed

The fix adds explicit rejection of same-timestamp execution in `AccessCheck`, introduces or uses marshaling fields that include `chainID` on the executing descriptor, applies a temporary fallback when older callers omit that chain ID, and replaces manual expiry addition with saturating arithmetic.

# Why It Matters

1. Reduces incorrect allow/deny decisions in access-list validation.

2. Makes the executing-chain context less ambiguous for interop checks.

3. Clarifies that intra-timestamp execution is not accepted by this validation path.

4. Removes a hand-written overflow check in favor of safer arithmetic.

# Evidence Notes

The strongest support is in `op-supervisor/supervisor/types/types.go`, `op-supervisor/supervisor/backend/backend.go`, and `op-supervisor/supervisor/backend/depset/links.go`. The commit message and code clearly indicate a validation fix around interop access-list checks and missing executing chain IDs. However, the supplied evidence does not show a demonstrated exploit, concrete impact, or whether the pre-patch behavior caused false accepts, false rejects, or only interoperability problems. Protocol security invariant: Access-list approval should use the correct executing-chain context and should only pass for execution times that satisfy the validator's ordering and expiry rules; same-timestamp execution is not considered safely verifiable in this check path. Verification notes: The patch does not prove a user-triggerable privilege escalation, theft, or consensus break. The backward-compatibility fallback for missing executing chain ID may partly be operational interoperability, not purely a security fix. The diff shows stricter admission checks for interop execution, but not a demonstrated end-to-end exploit path. It is not proven here whether the pre-patch behavior caused false accepts, false rejects, or both in production. `types_test.go` was updated with focused `ExecutingDescriptor.AccessCheck` coverage. The evidence supports a correctness or hardening change in validation logic. The provided snippets do not prove a user-triggerable security exploit or end-to-end protocol break. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `access-control-validation`
Final impact type: `policy-bypass-risk`
Final confidence: `medium`
Final tags: `blockchain-core, interop, access-list-validation, time-validation`

The patch is in a security-sensitive validation path and clearly tightens admission rules rather than just refactoring them. It adds an explicit reject case for same-timestamp execution because that case cannot be safely verified, makes executing-chain context explicit for interop checks, and replaces hand-rolled expiry arithmetic with a safer helper. The evidence does not prove a concrete exploitable vulnerability or real-world impact, so this is better kept as security hardening rather than a confirmed security fix.

## Security Evidence

1. `ExecutingDescriptor.AccessCheck` now rejects `ed.Timestamp == initMsgTimestamp` with `ErrConflict`, explicitly closing an ambiguous intra-timestamp case.
2. `CheckAccessList` now derives and uses the executing `ChainID`, reducing ambiguity in interop access-list validation.
3. `CanExecute` switches expiry computation to `safemath.SaturatingAdd`, hardening a security-relevant eligibility check against arithmetic edge cases.
4. Tests were added/updated around `ExecutingDescriptor.AccessCheck`, indicating intentional tightening of validation behavior.

## Missing Evidence

1. The patch does not show a concrete exploit, attacker model, or reachable abuse path.
2. There is no proof that pre-patch behavior enabled theft, privilege escalation, or consensus failure.
3. The backward-compatibility fallback suggests interoperability/correctness goals in addition to security hardening.

## Claim Boundaries

1. This supports retention as a hardening change in a security-sensitive validation path, not as a proven exploitable bug fix.
2. The evidence supports stricter access-list and execution-eligibility checks, not the original `serialization-or-state-representation` framing.
3. The patch alone does not justify claiming a demonstrated authorization bypass or end-to-end protocol compromise.
