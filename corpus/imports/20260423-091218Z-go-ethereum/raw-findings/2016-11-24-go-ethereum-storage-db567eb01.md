---
case_id: case_20161124_db567eb01
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2016-11-24
source_refs:
  - git:db567eb01d270c919377cca894e9e71a2b928e2c
  - "core/state/statedb_test.go:356"
  - "core/state/state_object.go:141"
  - "core/state/state_object.go:245"
  - "core/state/journal.go:91"
bug_class: consensus-state-revert-mismatch
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain
  - consensus
  - state-management
  - journal-revert
  - eip158
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a consensus-relevant StateDB journaling fix, not a broader exploit primitive. The patch adds explicit journaling and undo behavior for touched empty accounts during zero-value balance handling, with a RIPEMD precompile exception described by the commit as Parity compatibility.

## Observed Patch Facts

1. In `core/state/statedb_test.go`, the patch adds `func TestTouchDelete(t *testing.T) {`.

2. In `core/state/state_object.go`, the patch replaces `func (c *StateObject) getTrie(db trie.Database) *trie.SecureTrie {` with `func (c *StateObject) touch() {`.

3. In `core/state/state_object.go`, the patch replaces `if amount.Cmp(common.Big0) == 0 && !c.empty() {` with `if amount.Cmp(common.Big0) == 0 {`.

4. In `core/state/journal.go`, the patch replaces `func (ch balanceChange) undo(s *StateDB) {` with `var ripemd = common.HexToAddress("0000000000000000000000000000000000000003")`.

## Project Context

The changed code sits primarily in `core/state`, which anchors the finding in the `storage` area of the project. Historical context from `core/state/statedb.go`, `core/state/state_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/state/statedb.go`, `core/state/iterator.go`. The strongest project-level identifiers around this patch are `state`, `common`, `account`, and `prev`.

## Before/After Behavior

Before the patch, the shown zero-amount AddBalance path did not record a touch-specific journal entry for empty accounts, and no touchChange undo handler is shown. After the patch, zero-amount additions to empty accounts call touch(), touch() records the prior touched state and marks the object dirty, and touchChange.undo() removes newly touched objects from transient StateDB maps except for the RIPEMD precompile address. A regression test covers commit/reset/snapshot/AddBalance/revert behavior.

# Root Cause

Touched-account state could be introduced during EIP158 empty-account handling without a corresponding reversible journal entry. That could leave snapshot/revert behavior inconsistent with the intended consensus-compatible state transition.

## Walkthrough

1. StateObject.AddBalance handles a zero amount during EIP158 empty-account processing.

2. The patched zero-amount branch calls c.touch() when the account is empty.

3. StateObject.touch() appends a touchChange containing the account address and previous touched flag before setting touched to true and marking the object dirty.

4. journal.go adds touchChange.undo() to remove newly touched accounts from stateObjects and stateObjectsDirty.

5. The undo path excludes the hard-coded RIPEMD precompile address, matching the commit's stated Parity compatibility context.

6. TestTouchDelete exercises the touched-account behavior across commit, reset, snapshot, zero-value AddBalance, and revert.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state/state_object.go | 141 | adds StateObject.touch() to journal previous touched state and mark the object dirty |
| core/state/state_object.go | 245 | changes AddBalance zero-amount handling so empty accounts are touched for EIP158 clearing semantics |
| core/state/journal.go | 91 | adds touchChange undo logic to remove newly touched objects during snapshot revert, with RIPEMD precompile exception |
| core/state/statedb_test.go | 356 | adds regression coverage for touch/delete behavior across commit, reset, snapshot, and revert |

## Code Snippets

## Snippet 1

Context: `core/state/statedb_test.go:356` (changes signature or replay validation logic)

Before
```go
return nil
}
```
After
```go
return nil
}

func TestTouchDelete(t *testing.T) {
	db, _ := ethdb.NewMemDatabase()
	state, _ := New(common.Hash{}, db)
	state.GetOrNewStateObject(common.Address{})
	root, _ := state.Commit(false)
```

## Snippet 2

Context: `core/state/state_object.go:141` (changes persisted or aggregate state handling)

Before
```go
}

func (c *StateObject) getTrie(db trie.Database) *trie.SecureTrie {
	if c.trie == nil {
```
After
```go
}

func (c *StateObject) touch() {
	c.db.journal = append(c.db.journal, touchChange{
		account: &c.address,
		prev:    c.touched,
	})
	if c.onDirty != nil {
```

## Snippet 3

Context: `core/state/state_object.go:245` (changes a sensitive control or state-update path)

Before
```go
// EIP158: We must check emptiness for the objects such that the account
	// clearing (0,0,0 objects) can take effect.
	if amount.Cmp(common.Big0) == 0 && !c.empty() {
		return
	}
```
After
```go
// EIP158: We must check emptiness for the objects such that the account
	// clearing (0,0,0 objects) can take effect.
	if amount.Cmp(common.Big0) == 0 {
		if c.empty() {
			c.touch()
		}

		return
```

## Snippet 4

Context: `core/state/journal.go:91` (changes a sensitive control or state-update path)

Before
```go
}

func (ch balanceChange) undo(s *StateDB) {
	s.GetStateObject(*ch.account).setBalance(ch.prev)
```
After
```go
}

var ripemd = common.HexToAddress("0000000000000000000000000000000000000003")

func (ch touchChange) undo(s *StateDB) {
	if !ch.prev && *ch.account != ripemd {
		delete(s.stateObjects, *ch.account)
		delete(s.stateObjectsDirty, *ch.account)
```

# Fix Pattern

Represent consensus-visible transient state changes as journaled mutations with an explicit undo path, then add regression coverage around snapshot/revert boundaries.

## How It Was Fixed

The patch adds StateObject.touch(), calls it for zero-value AddBalance on empty accounts, adds touchChange.undo(), and adds TestTouchDelete regression coverage. The fix is limited to state journaling and client compatibility behavior shown in the provided evidence.

# Why It Matters

1. Consensus execution must remain deterministic across clients.

2. Snapshot/revert must undo touched-account state, not only balance or suicide state.

3. EIP158 empty-account handling affects consensus-visible state.

4. The evidence supports consensus divergence risk, not theft, signature bypass, memory corruption, or cryptographic failure.

# Evidence Notes

Grounded evidence comes from core/state/state_object.go adding touch(), core/state/state_object.go changing AddBalance zero-amount handling, core/state/journal.go adding touchChange.undo() with a RIPEMD exception, and core/state/statedb_test.go adding TestTouchDelete. The commit message explicitly calls this a consensus issue and mentions Parity compatibility. The supplied evidence does not establish a direct exploit path or prove funds loss. Protocol security invariant: Ethereum clients must apply EIP158 empty-account touch and snapshot/revert behavior deterministically so consensus-visible state remains compatible across clients and chain history. Verification notes: No direct exploit path is shown by the patch evidence. No proof of funds theft, signature bypass, or memory corruption is shown. The patch includes compatibility with a Parity consensus bug, so it does not prove the protocol behavior is intrinsically ideal. The evidence supports consensus/state-root divergence risk, not a cryptographic weakness. No independent execution or file inspection was performed. Classification relies only on the supplied diff excerpts and commit metadata. Confidence is medium because consensus relevance is well supported, but exploitability and vulnerability impact are not directly demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-revert-mismatch`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain, consensus, state-management, journal-revert, eip158`

The supplied evidence supports retaining this as a security-relevant consensus hardening case, but not confidently as a concrete exploitable security fix. The commit explicitly describes a consensus issue and Parity compatibility, and the patch changes Ethereum StateDB journaling, snapshot revert behavior, and EIP158 empty-account touch handling. That is security-sensitive because consensus divergence affects chain/state integrity, but the evidence does not prove a direct attacker-triggered exploit, funds loss, or cryptographic bypass.

## Security Evidence

1. Commit subject explicitly says fixed consensus issue.
2. Patch changes core Ethereum state transition and journaling behavior.
3. Zero-value AddBalance on empty accounts now records touch state for EIP158 semantics.
4. New touchChange undo removes newly touched accounts during snapshot revert.
5. Regression test covers commit, reset, snapshot, zero-value balance touch, and revert behavior.
6. RIPEMD precompile exception is tied to Parity consensus compatibility.

## Missing Evidence

1. No direct exploit path is shown.
2. No evidence of theft, authorization bypass, memory corruption, or signature failure.
3. No demonstration that an attacker could intentionally trigger a network split from the provided patch alone.
4. No external advisory or vulnerability identifier is provided.

## Claim Boundaries

1. Validate as consensus/state-integrity hardening, not a proven exploit fix.
2. Do not claim funds loss or account takeover.
3. Do not claim a cryptographic vulnerability.
4. Do not generalize beyond StateDB touch journaling, snapshot revert, EIP158 empty-account handling, and Parity compatibility.
