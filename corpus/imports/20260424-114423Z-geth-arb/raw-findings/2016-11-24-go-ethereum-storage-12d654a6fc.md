---
case_id: case_20161124_12d654a6fc
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
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
bug_class: consensus-state-divergence
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain-consensus
  - state-transition
  - state-journal
  - snapshot-revert
  - eip158
  - go-ethereum
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a security-relevant consensus-state fix in go-ethereum core state handling. It adds explicit journaling for touched account state, invokes that path for zero-value balance additions to empty accounts, and adds revert logic so snapshot rollback removes newly touched accounts from in-memory state maps, with a RIPEMD precompile exception. The evidence supports consensus compatibility and state-root integrity risk, not direct theft, privilege escalation, memory corruption, or cryptographic failure.

## Observed Patch Facts

1. In `core/state/statedb_test.go`, the patch adds `func TestTouchDelete(t *testing.T) {`.

2. In `core/state/state_object.go`, the patch replaces `func (c *StateObject) getTrie(db trie.Database) *trie.SecureTrie {` with `func (c *StateObject) touch() {`.

3. In `core/state/state_object.go`, the patch replaces `if amount.Cmp(common.Big0) == 0 && !c.empty() {` with `if amount.Cmp(common.Big0) == 0 {`.

4. In `core/state/journal.go`, the patch replaces `func (ch balanceChange) undo(s *StateDB) {` with `var ripemd = common.HexToAddress("0000000000000000000000000000000000000003")`.

## Project Context

The changed code sits primarily in `core/state`, which anchors the finding in the `storage` area of the project. Historical context from `core/state/statedb.go`, `core/state/state_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/state/statedb.go`, `core/state/iterator.go`. The strongest project-level identifiers around this patch are `state`, `common`, `account`, and `prev`.

## Before/After Behavior

Before the patch, the supplied AddBalance hunk returned early only for zero-value additions to non-empty accounts; zero-value additions to empty accounts were not shown as an explicit reversible touch operation. After the patch, AddBalance handles zero-value additions in one branch, calls touch() when the account is empty, and returns. The new touch() method records the prior touched flag in the journal, marks the object dirty, and sets touched=true. The new touchChange.undo removes newly touched accounts from stateObjects and stateObjectsDirty on revert, except for the RIPEMD precompile address. A regression test was added around touched empty account behavior after commit/reset, snapshot, zero-value AddBalance, and dirty-state observation.

# Root Cause

The supported root cause is incomplete journaling and undo handling for EIP158 touched empty accounts. A zero-value operation on an empty account could create consensus-relevant touched state, but that touch state was not represented as its own reversible journal entry, so snapshot/revert behavior could leave state inconsistent with the required consensus semantics.

## Walkthrough

1. EIP158 makes touched empty accounts relevant to account clearing and state transition behavior.

2. The pre-fix AddBalance logic shown did not explicitly journal a zero-value touch on an empty account.

3. The patch adds StateObject.touch(), which records the previous touched flag, marks the object dirty, and sets touched=true.

4. The patch changes AddBalance so zero-value additions to empty accounts call touch() before returning.

5. The patch adds touchChange.undo(), which removes newly touched accounts from stateObjects and stateObjectsDirty during revert unless the account is the RIPEMD precompile address.

6. The added test provides regression coverage for touched empty account handling around snapshot-style state changes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state/state_object.go | 141 | adds StateObject.touch journaling and dirty marking for touched account state |
| core/state/state_object.go | 245 | changes zero-value AddBalance handling to touch empty accounts for EIP158 account clearing semantics |
| core/state/journal.go | 91 | adds touchChange undo logic that removes non-previously-touched accounts from state object maps, with RIPEMD precompile exception |
| core/state/statedb_test.go | 356 | adds regression coverage for touched empty account deletion after snapshot revert |

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

Make a consensus-relevant no-op-looking state transition explicit in the journal, then restore the prior in-memory state during snapshot/revert, including required protocol compatibility exceptions.

## How It Was Fixed

The fix introduced a touchChange journal entry through StateObject.touch(), called that path from AddBalance for zero-value additions to empty accounts, and implemented touchChange undo logic that deletes newly touched accounts from stateObjects and stateObjectsDirty on revert while preserving the RIPEMD precompile exception.

# Why It Matters

1. Consensus clients must agree on state transitions and state roots.

2. Touched empty account handling is consensus-relevant under EIP158.

3. Snapshot/revert must undo touched-account side effects exactly.

4. The commit message explicitly identifies this as a consensus issue.

5. The evidence does not support claims beyond consensus/state integrity impact.

# Evidence Notes

Primary evidence comes from core/state/state_object.go, core/state/journal.go, and core/state/statedb_test.go. The commit message directly calls the change a consensus issue and mentions chain compatibility. The code supports a consensus-state divergence classification. Claims about reliable exploitability, direct asset theft, privilege escalation, memory safety, or cryptographic breakage are not supported by the provided evidence. Protocol security invariant: Ethereum consensus clients must apply the same state transition and derive the same state root for a block. EIP158 touched-empty-account behavior and StateDB snapshot/revert journaling must preserve consensus-visible account state exactly, including compatibility exceptions required by the active chain. Verification notes: The patch does not prove direct theft, privilege escalation, or memory-safety exploitation. The evidence does not show a cryptographic primitive failure. The evidence does not prove an attacker could reliably trigger a chain split, only that consensus state handling differed and was fixed for chain compatibility. The RIPEMD exception is shown as consensus compatibility behavior, not as a standalone vulnerability. The patch scope is EIP158 touched-account and journal-revert semantics, not arbitrary state database corruption. Confirmed by commit metadata describing a consensus issue. Confirmed by StateObject.touch journaling added in core/state/state_object.go. Confirmed by AddBalance zero-value empty-account touch handling. Confirmed by touchChange.undo revert behavior in core/state/journal.go. Regression coverage is indicated by the added TestTouchDelete path, though only partial test body is provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-state-divergence`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-consensus, state-transition, state-journal, snapshot-revert, eip158, go-ethereum`

The supplied evidence supports retaining this as a security-relevant consensus fix, but the original metadata is somewhat too broad and confident. The commit message explicitly identifies a consensus issue and chain-sync compatibility, while the patch changes Ethereum state transition behavior for touched empty accounts, journals that touch state, and adds undo behavior for snapshot reverts. That is enough for a consensus/state-integrity security-fix classification, though the evidence does not prove exploitability, theft, or a concrete attacker-triggered chain split.

## Security Evidence

1. Commit subject says a consensus issue was fixed and touch revert was added.
2. Commit body says the change was needed to remain in sync with the current longest chain.
3. Patch changes core state handling for EIP158 touched empty accounts.
4. New touch journal entry records prior touched state before marking an account touched.
5. New undo logic removes newly touched accounts from state maps during revert, with a protocol compatibility exception.
6. Regression test coverage was added for touched account deletion behavior around commit/reset/snapshot.

## Missing Evidence

1. No advisory, CVE, or explicit attacker scenario is provided.
2. Patch does not demonstrate direct asset theft, privilege escalation, memory corruption, or cryptographic compromise.
3. Evidence does not prove a reliably triggerable chain split, only consensus-sensitive divergence/compatibility risk.
4. Only partial test body is shown.

## Claim Boundaries

1. Classify as a consensus/state-integrity fix, not a general database corruption flaw.
2. Do not claim direct financial theft or arbitrary state modification from the supplied evidence.
3. Do not claim cryptographic failure or memory safety impact.
4. The RIPEMD exception should be treated as consensus compatibility behavior, not a standalone vulnerability.
