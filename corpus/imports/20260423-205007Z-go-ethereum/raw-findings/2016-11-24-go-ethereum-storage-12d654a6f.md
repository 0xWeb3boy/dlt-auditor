---
case_id: case_20161124_12d654a6f
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
  - git:12d654a6fc4580f9194a931032ebf0e1b1927279
  - "core/state/statedb_test.go:356"
  - "core/state/state_object.go:141"
  - "core/state/state_object.go:245"
  - "core/state/journal.go:91"
bug_class: consensus-state-revert-bug
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain
  - consensus
  - state-transition
  - snapshot-revert
  - eip158
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is best classified as a likely consensus-security fix in go-ethereum core/state. It makes account touch state explicit, journaled, and reversible so zero-value operations on empty accounts interact correctly with EIP158 clearing and Snapshot/Revert behavior. The evidence supports consensus-state compatibility risk, but not claims of theft, cryptographic failure, memory corruption, or proven exploitability.

## Observed Patch Facts

1. In `core/state/statedb_test.go`, the patch adds `func TestTouchDelete(t *testing.T) {`.

2. In `core/state/state_object.go`, the patch replaces `func (c *StateObject) getTrie(db trie.Database) *trie.SecureTrie {` with `func (c *StateObject) touch() {`.

3. In `core/state/state_object.go`, the patch replaces `if amount.Cmp(common.Big0) == 0 && !c.empty() {` with `if amount.Cmp(common.Big0) == 0 {`.

4. In `core/state/journal.go`, the patch replaces `func (ch balanceChange) undo(s *StateDB) {` with `var ripemd = common.HexToAddress("0000000000000000000000000000000000000003")`.

## Project Context

The changed code sits primarily in `core/state`, which anchors the finding in the `storage` area of the project. Historical context from `core/state/statedb.go`, `core/state/state_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/state/statedb.go`, `core/state/iterator.go`. The strongest project-level identifiers around this patch are `state`, `common`, `account`, and `prev`.

## Before/After Behavior

Before the patch, the provided AddBalance(0) evidence did not show a dedicated journaled touch transition for empty accounts, and no touchChange undo implementation was present in the supplied journal hunk. After the patch, AddBalance(0) touches empty accounts, StateObject.touch() journals the previous touched flag and marks the object dirty/touched, and touchChange.undo() removes newly touched accounts from in-memory state tracking on revert except for the RIPEMD precompile address.

# Root Cause

Touching an account was consensus-relevant under the shown EIP158 empty-account clearing path, but the pre-fix behavior did not represent that touch as an independently journaled and revertible state transition. Snapshot/Revert could therefore leave account existence or dirty-state inconsistent with the intended state transition behavior.

## Walkthrough

1. StateObject.AddBalance contains special handling for zero-value balance operations under EIP158 empty-account clearing semantics.

2. The patch adds StateObject.touch(), which records a touchChange with the account address and previous touched state before setting touched state.

3. AddBalance(0) now calls touch() when the target account is empty, then returns without applying a normal balance update.

4. The journal now has touchChange.undo(), which deletes newly touched non-RIPEMD accounts from stateObjects and stateObjectsDirty during revert.

5. The added TestTouchDelete exercises commit, reset, snapshot, zero-value AddBalance, dirty-state behavior, and touched-account revert behavior.

6. The commit message explicitly frames the change as fixing a consensus issue and matching Parity behavior to stay on the longest chain.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state/state_object.go | 141 | Adds StateObject.touch() to journal the previous touched state and mark the object dirty/touched. |
| core/state/state_object.go | 245 | Changes AddBalance(0) handling so empty accounts are touched for EIP158 clearing semantics instead of returning without recording the touch. |
| core/state/journal.go | 91 | Adds touchChange undo behavior to restore state after Snapshot/Revert, with a RIPEMD precompile exception for client compatibility. |
| core/state/statedb_test.go | 356 | Adds regression coverage for touched account deletion/revert behavior after commit/reset/snapshot. |

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

Model implicit consensus-relevant state as an explicit journal entry, mutate it through one helper, and implement undo logic so snapshot rollback restores account tracking consistently.

## How It Was Fixed

The change introduced a touchChange journal entry and StateObject.touch() helper, routed empty-account AddBalance(0) through that helper, added touchChange undo behavior, and added regression coverage for touch/delete behavior. The RIPEMD exception is supported as compatibility behavior by the supplied code and commit context, but the evidence does not establish a broader protocol rule for it.

# Why It Matters

1. Consensus clients must agree on post-state computation.

2. EIP158 empty-account clearing affects account existence.

3. Incorrect revert handling can change subsequent state execution results.

4. The commit message identifies this as a consensus issue.

5. Evidence does not establish direct attacker exploitability.

# Evidence Notes

The strongest evidence is the state_object.go AddBalance(0) change, the new StateObject.touch() helper, the journal.go touchChange.undo() implementation, the TestTouchDelete regression test, and the commit message naming a consensus issue. Claims should remain limited to consensus-state/revert correctness; exploitability and financial impact are not proven by the supplied material. Protocol security invariant: Ethereum state transition execution must produce the same post-state across clients for EIP158 empty-account clearing, including when execution uses Snapshot/Revert. If an empty account is touched by a zero-value balance operation, that touch state must be recorded and reverted consistently. Verification notes: The patch does not prove remote exploitability or attacker control over a chain split scenario. The patch does not show theft, signature bypass, cryptographic breakage, or memory corruption. The RIPEMD exception appears to preserve consensus compatibility with an existing client behavior, not to enforce an ideal protocol rule. Only the provided hunks support the classification; touched files outside the evidence are not independently assessed. No commands or external context were used. Classification relies only on supplied hunks, commit metadata, mapper output, and draft text. Security verdict is likely rather than confirmed because practical exploitability is not demonstrated. The RIPEMD exception is treated only as consensus compatibility behavior supported by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-state-revert-bug`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain, consensus, state-transition, snapshot-revert, eip158`

The supplied evidence supports retaining this as a security-relevant consensus/state-transition fix, but the original finding is too confident. The patch changes core Ethereum state semantics for empty-account touches, journals touch state, and adds undo behavior for Snapshot/Revert, while the commit message explicitly calls it a consensus issue and mentions syncing with the longest chain. That is security-relevant for a blockchain client because inconsistent state transition results can affect consensus integrity. The evidence does not prove exploitability, theft, or a concrete adversarial trigger, so the classification should remain likely with medium confidence and bounded to consensus/state integrity.

## Security Evidence

1. Commit subject explicitly says a consensus issue was fixed.
2. Commit body says the change was needed to remain in sync with the current longest chain.
3. Patch changes EIP158 empty-account handling in AddBalance(0), a consensus-state transition path.
4. Patch adds journaled touch state and undo behavior for Snapshot/Revert consistency.
5. Regression test exercises touch/delete/revert behavior around committed state.

## Missing Evidence

1. No supplied evidence shows attacker-controlled exploitation.
2. No supplied evidence shows theft, fund loss, signature bypass, or cryptographic failure.
3. No supplied evidence proves a real chain split occurred because of the pre-fix behavior.
4. No broader protocol explanation is provided beyond the patch and commit metadata.

## Claim Boundaries

1. Valid claim: consensus-relevant state handling for touched empty accounts was corrected or made client-compatible.
2. Valid claim: Snapshot/Revert behavior for touch state became explicitly journaled and reversible.
3. Do not claim proven remote exploitability from the supplied evidence.
4. Do not claim financial loss or account compromise.
5. Treat the RIPEMD exception as compatibility behavior only, not as a separately proven security rule.
