---
case_id: case_20260305_26dc364ff
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
impact_type:
  - state-integrity
source_quality: medium
date: 2026-03-05
source_refs:
  - git:26dc364ff5a868d53087d5cb03edb8381c13ef94
  - "eth/downloader/whitelist/milestone_test.go:61"
  - "eth/bor_api_backend.go:48"
  - "eth/downloader/whitelist/service.go:80"
  - "eth/bor_api_backend.go:66"
bug_class: integer-overflow
confidence: medium
tags:
  - blockchain-core
  - consensus
  - rpc
  - database
  - integer-overflow
  - state-sanitization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly fixes out-of-range block-number handling in Bor milestone lock/sync logic, but the provided evidence does not establish a concrete security vulnerability or attacker-controlled trigger. The strongest supported claim is robustness hardening around overflow-prone arithmetic and corrupted persisted lock state.

## Observed Patch Facts

1. In `eth/downloader/whitelist/milestone_test.go`, the patch replaces `// TestMilestoneUnlockSprintRace exercises concurrent readers and writers` with `// TestIsReorgAllowedWithMaxLockedNumber verifies that IsReorgAllowed correctly`.

2. In `eth/bor_api_backend.go`, the patch replaces `func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, starBlockNr uint64, endBlo...` with `func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, _ uint64, endBlockNr uint6...`.

3. In `eth/downloader/whitelist/service.go`, the patch replaces `order, list, err := rawdb.ReadFutureMilestoneList(db)` with `// Discard the locked state if the stored milestone number is out of the safe range (...`.

4. In `eth/bor_api_backend.go`, the patch replaces `// Confirmation of 16 blocks on the endblock` with `// Confirmation of tipConfirmationOffset blocks on the endblock`.

## Project Context

The changed code sits primarily in `eth/downloader/whitelist`, `eth/downloader`, which anchors the finding in the `consensus` area of the project. Historical context from `eth/downloader/whitelist/milestone.go`, `eth/downloader/whitelist/service_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/downloader/whitelist/service_test.go`, `eth/downloader/whitelist/milestone.go`. The strongest project-level identifiers around this patch are `uint64`, `endBlockNr`, `locked`, and `lockedMilestoneNumber`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/supply_test.go`, `eth/tracers/internal/tracetest/prestate_test.go`.

## Before/After Behavior

Before the patch, `GetVoteOnHash` added the confirmation offset to `endBlockNr` without first rejecting values near the maximum safe range, and service startup accepted persisted locked milestone numbers unless lock-field loading failed. After the patch, `GetVoteOnHash` rejects oversized `endBlockNr` values, requires the confirmation block lookup to return a non-nil block, and `NewService` clears persisted locked milestone state when `lockedMilestoneNumber` exceeds `math.MaxInt64`.

# Root Cause

Missing range validation for block-height values and trust in persisted lock metadata that could be outside the safe block-number range used by later logic.

## Walkthrough

1. `GetVoteOnHash` now checks `endBlockNr > math.MaxInt64-tipConfirmationOffset` before adding the offset.

2. That check prevents the derived confirmation height from being formed from an out-of-range input.

3. The same function also now treats a nil confirmation block as invalid instead of only checking for an error.

4. `NewService` now inspects persisted lock state from `rawdb.ReadLockField(db)` and treats `lockedMilestoneNumber > math.MaxInt64` as invalid.

5. When such persisted state is found, the code clears the lock fields and writes the repaired state back to the database.

6. The added test documents the intended behavior for an extremely large locked milestone number in reorg-related logic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/bor_api_backend.go | 50 | Bor API vote lookup now rejects out-of-range `endBlockNr` before confirmation-offset arithmetic and block retrieval. |
| eth/bor_api_backend.go | 66 | Confirmation-block existence check now uses the validated post-offset height, preventing wrapped or invalid lookups from driving sync/vote flow. |
| eth/downloader/whitelist/service.go | 80 | Whitelist service startup sanitizes persisted locked milestone state and clears invalid oversized lock records from DB. |
| eth/downloader/whitelist/milestone_test.go | 61 | Regression test asserts reorg allowance stays false when the locked milestone number is unrealistically large. |

## Code Snippets

## Snippet 1

Context: `eth/downloader/whitelist/milestone_test.go:61` (changes signature or replay validation logic)

Before
```go
}

// TestMilestoneUnlockSprintRace exercises concurrent readers and writers
// of milestone lock state and future milestone lists.
```
After
```go
}

// TestIsReorgAllowedWithMaxLockedNumber verifies that IsReorgAllowed correctly
// handles the case where LockedMilestoneNumber is set to an extremely large value.
// No real chain tip can exceed such a number, so IsReorgAllowed must return false.
func TestIsReorgAllowedWithMaxLockedNumber(t *testing.T) {
	db := rawdb.NewMemoryDatabase()
	svc := NewService(db, false, 0)
```

## Snippet 2

Context: `eth/bor_api_backend.go:48` (changes signature or replay validation logic)

Before
```go
// GetVoteOnHash returns the vote on hash
func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, starBlockNr uint64, endBlockNr uint64, hash string, milestoneId string) (bool, error) {
	var api *bor.API
```
After
```go
// GetVoteOnHash returns the vote on hash
func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, _ uint64, endBlockNr uint64, hash string, milestoneId string) (bool, error) {
	// Reject invalid block numbers (overflowing with the confirmation offset or exceeding the valid range).
	if endBlockNr > math.MaxInt64-tipConfirmationOffset {
		return false, errInvalidBlockNumber
	}
```

## Snippet 3

Context: `eth/downloader/whitelist/service.go:80` (changes signature or replay validation logic)

Before
```go
}

	order, list, err := rawdb.ReadFutureMilestoneList(db)
	if err != nil {
```
After
```go
}

	// Discard the locked state if the stored milestone number is out of the safe range (corrupted data).
	if locked && lockedMilestoneNumber > math.MaxInt64 {
		log.Warn("Discarding invalid locked milestone loaded from DB", "lockedMilestoneNumber", lockedMilestoneNumber)
		locked = false
		lockedMilestoneNumber = 0
		lockedMilestoneHash = common.Hash{}
```

## Snippet 4

Context: `eth/bor_api_backend.go:66` (changes a sensitive control or state-update path)

Before
```go
}

	// Confirmation of 16 blocks on the endblock
	tipConfirmationBlockNr := endBlockNr + uint64(16)

	// Check if tipConfirmation block exit
	_, err := b.BlockByNumber(ctx, rpc.BlockNumber(tipConfirmationBlockNr))
	if err != nil {
```
After
```go
}

	// Confirmation of tipConfirmationOffset blocks on the endblock
	tipConfirmationBlockNr := endBlockNr + tipConfirmationOffset

	// Check if the tipConfirmation block exists
	tipBlock, err := b.BlockByNumber(ctx, rpc.BlockNumber(tipConfirmationBlockNr))
	if err != nil || tipBlock == nil {
```

# Fix Pattern

Add explicit upper-bound validation before block-number arithmetic and sanitize persisted state that falls outside the accepted numeric domain.

## How It Was Fixed

The fix rejects oversized `endBlockNr` inputs in `GetVoteOnHash`, strengthens the confirmation-block existence check, and clears invalid persisted milestone lock state during service initialization so that out-of-range values do not continue affecting runtime decisions.

# Why It Matters

1. Prevents malformed or corrupted large block numbers from flowing into control logic.

2. Reduces the chance that persisted invalid lock state survives restarts.

3. Improves correctness in consensus-adjacent milestone and sync handling.

4. Does not, by itself, prove exploitability or a confirmed security impact.

# Evidence Notes

Supported directly by the diff: `eth/bor_api_backend.go` adds a `math.MaxInt64-tipConfirmationOffset` guard and a non-nil confirmation-block check; `eth/downloader/whitelist/service.go` discards persisted locked milestone numbers above `math.MaxInt64`; `eth/downloader/whitelist/milestone_test.go` adds a regression test for an extremely large locked milestone number. Not supported by the evidence: remote attacker control, confirmed consensus break, or proof that this was an exploitable vulnerability rather than correctness hardening. Protocol security invariant: Milestone lock and vote/sync checks should only use block numbers that remain within the safe block-number range expected by downstream APIs, and persisted lock state should not carry out-of-range milestone numbers into runtime reorg decisions. Verification notes: The patch does not prove a remotely reachable attacker can supply the oversized values. The patch does not show confirmed consensus failure or finalized-state violation, only incorrect lock/sync handling risk. The patch treats oversized persisted lock data as corrupted state but does not prove how that corruption is introduced. The patch text supports an overflow/range-handling fix. The patch text supports persisted-state sanitization on startup. The security relevance remains unproven from the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, rpc, database, integer-overflow, state-sanitization`

The patch shows explicit hardening in security-sensitive consensus and sync code: it rejects overflow-prone block numbers before arithmetic, requires the confirmation block to actually exist, and sanitizes persisted milestone lock state that falls outside the safe numeric range. That is enough to support retaining this as security hardening in a blockchain-core corpus. However, the diff does not prove attacker control, exploitability, or a concrete consensus break, so it should not be labeled a confirmed security fix.

## Security Evidence

1. `GetVoteOnHash` now rejects `endBlockNr` values that would overflow when adding the confirmation offset.
2. The same path now treats a nil confirmation block as invalid instead of only checking for an error.
3. `NewService` clears persisted locked milestone state when `lockedMilestoneNumber > math.MaxInt64`.
4. The commit message explicitly says an overflow affected milestone lock and syncing.
5. The added test documents a reorg-related case with an extremely large locked milestone number.

## Missing Evidence

1. No proof that an external attacker can supply the oversized values through a reachable interface.
2. No evidence of a demonstrated exploit, chain split, or finalized-state violation.
3. No proof of how the corrupted persisted lock state could be introduced in practice.
4. No advisory, CVE, or explicit security impact statement in the provided material.

## Claim Boundaries

1. Supported claim: the patch hardens overflow/range handling in consensus-adjacent milestone and sync logic.
2. Supported claim: the patch sanitizes invalid persisted lock metadata on startup.
3. Not supported: a confirmed exploitable vulnerability.
4. Not supported: guaranteed remote trigger or proven consensus compromise.
