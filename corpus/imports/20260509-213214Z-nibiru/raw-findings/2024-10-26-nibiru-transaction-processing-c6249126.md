---
case_id: case_20241026_c6249126
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
impact_type:
  - state-integrity
source_quality: high
date: 2024-10-26
source_refs:
  - git:c62491262eeef1ecb1d179dc7f0ab95fc375ef6b
  - "x/evm/statedb/statedb.go:593"
  - "x/evm/precompile/precompile.go:191"
  - "x/evm/statedb/statedb.go:255"
  - "x/evm/statedb/statedb.go:506"
bug_class: precompile-rollback-hardening
confidence: medium
tags:
  - evm
  - precompile
  - rollback
  - state-integrity
  - transaction-context
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to correct precompile rollback and transaction-context handling by moving PrecompileCalled snapshots into the main StateDB journal, checking snapshot-save errors, and using evmTxCtx for account reads and commit. The evidence supports a state-consistency fix in a sensitive EVM precompile path, but it does not establish a concrete vulnerability, exploit path, value impact, or consensus/security failure. Treat this as security-relevant unclear rather than a confirmed or likely vulnerability fix.

## Observed Patch Facts

1. In `x/evm/statedb/statedb.go`, the patch replaces `func (s *StateDB) SavePrecompileSnapshotToJournal(` with `func (s *StateDB) SavePrecompileCalledJournalChange(`.

2. In `x/evm/precompile/precompile.go`, the patch replaces `cacheCtx, snapshot := stateDB.CacheCtxForPrecompile(contract.Address())` with `// journalEntry captures the state before precompile execution to enable`.

3. In `x/evm/statedb/statedb.go`, the patch replaces `if s.keeper.IsPrecompile(addr) {` with `// If no live objects are available, load it from keeper`.

4. In `x/evm/statedb/statedb.go`, the patch replaces `func (s *StateDB) Commit() error {` with `//`.

## Project Context

The changed code sits primarily in `x/evm/statedb`, `x/evm`, `x/evm/precompile`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/statedb/statedb_test.go`, `x/evm/statedb/state_object.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/statedb/statedb_test.go`, `x/evm/statedb/state_object.go`. The strongest project-level identifiers around this patch are `contract`, `stateDB`, `snapshot`, and `StateDB`. Nearby tests or test-like files include `x/evm/evmtest/smart_contract_test.go`, `x/evm/precompile/test/export.go`.

## Before/After Behavior

Before the patch, OnRunStart created a precompile cache context and saved a snapshot through SavePrecompileSnapshotToJournal without checking the returned error at the call site. That helper appended through a precompile state-object journal path, while getStateObject special-cased precompile addresses as synthetic live objects and some paths used s.ctx or GetContext. After the patch, OnRunStart obtains a PrecompileCalled journal entry from CacheCtxForPrecompile, saves it through SavePrecompileCalledJournalChange with error handling, appends it directly to s.Journal, tracks multistore cache count, loads accounts from s.evmTxCtx, and commits through GetEvmTxContext.

# Root Cause

The supplied evidence suggests the old implementation had an inconsistent rollback and context boundary for precompile SDK multistore side effects: precompile snapshots were routed through an object-level path and surrounding state access or commit paths could use an older context rather than the EVM transaction context. The evidence does not prove that this inconsistency was exploitable.

## Walkthrough

1. Precompile execution enters x/evm/precompile/precompile.go OnRunStart.

2. The code obtains a cache context and PrecompileCalled snapshot from StateDB.CacheCtxForPrecompile.

3. Before the patch, the snapshot was saved through SavePrecompileSnapshotToJournal, which appended through a precompile state-object journal path.

4. The old OnRunStart call did not check the helper's returned error in the shown hunk.

5. The old getStateObject path special-cased precompile addresses as synthetic objects and loaded accounts from s.ctx.

6. After the patch, SavePrecompileCalledJournalChange appends PrecompileCalled directly to the StateDB journal and returns an error if the multistore cache limit is exceeded.

7. OnRunStart now returns that error before precompile execution continues.

8. Related paths now use evmTxCtx for account loading and final commit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/statedb/statedb.go | 575 | creates transaction-scoped cache context for precompile execution and records the PrecompileCalled journal change used for rollback |
| x/evm/precompile/precompile.go | 180 | starts precompile execution by taking the cache context snapshot and saving it to the StateDB journal before downstream mutation |
| x/evm/statedb/statedb.go | 251 | loads account state from evmTxCtx instead of treating precompile addresses as synthetic live objects or reading from the prior context |
| x/evm/statedb/statedb.go | 501 | commits dirty StateDB changes through the EVM transaction context when precompile cache synchronization is needed |

## Code Snippets

## Snippet 1

Context: `x/evm/statedb/statedb.go:593` (changes persisted or aggregate state handling)

Before
```go
//
// See [PrecompileCalled] for more info.
func (s *StateDB) SavePrecompileSnapshotToJournal(
	precompileAddr common.Address,
	snapshot PrecompileCalled,
) error {
	obj := s.getOrNewStateObject(precompileAddr)
	obj.db.Journal.append(snapshot)
```
After
```go
//
// See [PrecompileCalled] for more info.
func (s *StateDB) SavePrecompileCalledJournalChange(
	precompileAddr common.Address,
	journalChange PrecompileCalled,
) error {
	s.Journal.append(journalChange)
	s.multistoreCacheCount++
```

## Snippet 2

Context: `x/evm/precompile/precompile.go:191` (changes persisted or aggregate state handling)

Before
```go
return
	}
	cacheCtx, snapshot := stateDB.CacheCtxForPrecompile(contract.Address())
	stateDB.SavePrecompileSnapshotToJournal(contract.Address(), snapshot)
	if err = stateDB.CommitCacheCtx(); err != nil {
		return res, fmt.Errorf("error committing dirty journal entries: %w", err)
```
After
```go
return
	}

	// journalEntry captures the state before precompile execution to enable
	// proper state reversal if the call fails or if [statedb.JournalChange]
	// is reverted in general.
	cacheCtx, journalEntry := stateDB.CacheCtxForPrecompile(contract.Address())
	if err = stateDB.SavePrecompileCalledJournalChange(contract.Address(), journalEntry); err != nil {
```

## Snippet 3

Context: `x/evm/statedb/statedb.go:255` (changes signature or replay validation logic)

Before
```go
}

	if s.keeper.IsPrecompile(addr) {
		obj := newObject(s, addr, Account{
			Nonce: 0,
		})
		obj.IsPrecompile = true
		s.setStateObject(obj)
```
After
```go
}

	// If no live objects are available, load it from keeper
	account := s.keeper.GetAccount(s.evmTxCtx, addr)
	if account == nil {
		return nil
```

## Snippet 4

Context: `x/evm/statedb/statedb.go:506` (changes a sensitive control or state-update path)

Before
```go
// StateDB object cannot be reused after [Commit] has completed. A new
// object needs to be created from the EVM.
func (s *StateDB) Commit() error {
	if s.writeToCommitCtxFromCacheCtx != nil {
		// cacheCtxSyncNeeded: If a precompile was called, a [JournalChange]
		// of type [PrecompileSnapshotBeforeRun] gets added and we branch off a
		// cache of the commit context (s.ctx).
		s.writeToCommitCtxFromCacheCtx()
```
After
```go
// StateDB object cannot be reused after [Commit] has completed. A new
// object needs to be created from the EVM.
//
// cacheCtxSyncNeeded: If one of the [Nibiru-Specific Precompiled Contracts] was
// called, a [JournalChange] of type [PrecompileSnapshotBeforeRun] gets added and
// we branch off a cache of the commit context (s.evmTxCtx).
//
// [Nibiru-Specific Precompiled Contracts]: https://nibiru.fi/docs/evm/precompiles/nibiru.html
```

# Fix Pattern

Move precompile multistore snapshot handling onto the transaction-scoped StateDB journal, propagate errors from snapshot/journal setup, and consistently use the EVM transaction context for account reads and commit.

## How It Was Fixed

The patch replaces SavePrecompileSnapshotToJournal with SavePrecompileCalledJournalChange, appends PrecompileCalled directly to s.Journal, tracks multistoreCacheCount, checks the save error in OnRunStart, removes the shown synthetic precompile-object branch from getStateObject, and switches account reads and commit behavior to evmTxCtx/GetEvmTxContext.

# Why It Matters

1. Precompile calls can mutate SDK-side multistore state outside ordinary EVM storage.

2. Rollback and commit boundaries are sensitive in transaction execution.

3. Unchecked snapshot-save errors could allow execution to continue after rollback bookkeeping failed.

4. The supplied evidence shows consistency hardening, but not a demonstrated exploit.

# Evidence Notes

Grounded evidence comes from x/evm/statedb/statedb.go around CacheCtxForPrecompile, SavePrecompileCalledJournalChange, getStateObject, and Commit, plus x/evm/precompile/precompile.go OnRunStart. Comments explicitly describe proper reversal if a precompile call fails or a JournalChange is reverted. The commit subject mentions NibiruBankKeeper transfer safety and tests, but the supplied hunks do not establish a separate bank-transfer vulnerability or include the test body. No concrete attacker action, asset impact, unauthorized state transition, or consensus failure is shown. Protocol security invariant: EVM transaction execution should keep EVM StateDB changes and SDK multistore mutations made by Nibiru-specific precompiles on the same transaction-scoped rollback and commit boundary, so failed or reverted precompile execution does not leave inconsistent side effects. Verification notes: No concrete exploit transaction is shown by the patch evidence. No attacker-controlled theft, mint, or consensus failure is proven directly. The evidence does not prove that all precompiles could violate rollback semantics, only that this path was corrected for precompile multistore side effects. The NibiruBankKeeper transfer-safety changes are mentioned in the commit subject but not sufficiently shown in the provided hunks to classify separately. Resource-exhaustion risk from the cache-count limit is possible but not independently proven as the main bug. Downgraded confidence from high to medium because exploitability is not evidenced. Downgraded security_verdict from likely to unclear because the vulnerability thesis is plausible but not established by the provided hunks. Set keep_in_security_corpus to false under the instruction for security-relevant but unproven fixes. Removed unsupported claims of confirmed protocol security impact, theft, minting, or consensus failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `precompile-rollback-hardening`
Final confidence: `medium`
Final tags: `evm, precompile, rollback, state-integrity, transaction-context, security-hardening`

The supplied patch evidence does not prove a concrete exploitable vulnerability, but it does clearly tighten security-sensitive transaction execution behavior in an EVM/precompile path. The changes move precompile multistore snapshots into the main StateDB journal, propagate failure from journal setup, use the EVM transaction context for account reads and commit, and comments explicitly frame the change as necessary for proper reversal of precompile side effects. This supports retaining it as security-hardening, not as a confirmed security-fix.

## Security Evidence

1. Precompile execution now saves a journal entry before running and returns an error if saving it fails.
2. The new comments explicitly state the journal entry enables proper state reversal if a precompile call fails or is reverted.
3. Precompile multistore snapshot handling moved from an object-level path to the main StateDB journal.
4. Account reads and commit paths now use evmTxCtx/GetEvmTxContext, aligning precompile side effects with transaction-scoped state.
5. The changed subsystem is EVM transaction processing and precompile state handling, a security-sensitive blockchain execution path.

## Missing Evidence

1. No exploit transaction or attacker-controlled sequence is shown.
2. No demonstrated theft, unauthorized transfer, mint, consensus failure, or persistent state corruption is included.
3. The commit subject mentions NIBI transfer safety, but the supplied hunks do not show enough transfer-specific evidence to validate that claim.
4. Regression test details are referenced but not supplied in full.

## Claim Boundaries

1. Validate only as security-hardening, not a confirmed vulnerability fix.
2. Do not claim concrete asset loss, theft, minting, or consensus failure from the provided evidence.
3. Do not generalize beyond Nibiru-specific precompile rollback and transaction-context handling.
4. The impact should remain limited to state integrity and rollback/commit consistency in transaction processing.
