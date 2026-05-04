---
case_id: case_20230927_8e6f2f83e6
project: avalanchego
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: hardening-or-correctness-fix
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - transaction-processing
  - hardening-or-correctness-fix
  - correctness-or-hardening
  - consensus
date: 2023-09-27
source_refs:
  - git:8e6f2f83e6b330050605bf21c389520964e86a2f
  - "core/predicate_check_test.go:311"
  - "core/predicate_check.go:39"
  - "core/predicate_check_test.go:111"
  - "core/predicate_check_test.go:78"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a fail-closed check in `CheckPredicates` so missing predicate context returns `ErrMissingPredicateContext` when predicate verification is required. The strongest supported claim is a security-relevant validation hardening in predicate/block validation, not a proven exploitable vulnerability.

## Observed Patch Facts

1. In `core/predicate_check_test.go`, the patch replaces `predicateContext := &precompileconfig.PredicateContext{` with `predicateRes, err := CheckPredicates(rules, test.predicateContext, tx)`.

2. In `core/predicate_check.go`, the patch replaces `for address, predicates := range predicateArguments {` with `// If there are no predicates to verify, return early and skip requiring the proposer...`.

3. In `core/predicate_check_test.go`, the patch replaces `expectedRes: map[common.Address][]byte{` with `expectedErr: ErrMissingPredicateContext,`.

4. In `core/predicate_check_test.go`, the patch replaces `"predicate named by access list returns empty": {` with `"predicate, no access list, no block context passes": {`.

## Project Context

Historical context from `core/state_transition.go`, `core/state_processor.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/evm.go`, `core/state_transition.go`. The strongest project-level identifiers around this patch are `predicateContext`, `precompileconfig`, `predicate`, and `expectedErr`.

## Before/After Behavior

Before the patch, tests always supplied a block context through the harness, and at least one access-list predicate case expected success even when the updated behavior now treats missing context as an error. After the patch, tests pass per-case predicate context, missing-context cases can be exercised directly, and cases where an access list names a predicate without proposer VM block context expect `ErrMissingPredicateContext`. Cases with no predicate work remain expected to pass without context.

# Root Cause

`CheckPredicates` lacked an explicit validation step ensuring that required predicate context was present before predicate verification work continued.

## Walkthrough

1. `CheckPredicates` validates intrinsic gas for the transaction.

2. It initializes predicate results and returns early when no predicates are configured.

3. It derives predicate arguments from the transaction access list.

4. The patch adds a missing-context guard that returns `ErrMissingPredicateContext` when `predicateContext` or `predicateContext.ProposerVMBlockCtx` is nil.

5. The tests now provide predicate context per table case instead of always constructing a valid context in the harness.

6. A predicate-named access-list case without block context now expects an error.

7. Tests also document that missing context is allowed when no predicate verification is needed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/predicate_check.go | 21 | CheckPredicates computes intrinsic gas, prepares predicate storage slots from the transaction access list, and now rejects missing predicate context when predicates require verification. |
| core/predicate_check_test.go | 28 | Table-driven predicate validation tests define cases where no predicates or no access-list predicate arguments may pass without context. |
| core/predicate_check_test.go | 105 | Test case now expects ErrMissingPredicateContext when an access list names a predicate but block context is absent. |
| core/predicate_check_test.go | 305 | Test harness now supplies per-case predicateContext and asserts expected errors before comparing predicate results. |

## Code Snippets

## Snippet 1

Context: `core/predicate_check_test.go:311` (changes a sensitive control or state-update path)

Before
```go
Gas:        test.gas,
			})
			predicateContext := &precompileconfig.PredicateContext{
				ProposerVMBlockCtx: &block.Context{
					PChainHeight: 10,
				},
			}
			predicateRes, err := CheckPredicates(rules, predicateContext, tx)
```
After
```go
Gas:        test.gas,
			})
			predicateRes, err := CheckPredicates(rules, test.predicateContext, tx)
			require.ErrorIs(err, test.expectedErr)
			if test.expectedErr != nil {
				return
			}
```

## Snippet 2

Context: `core/predicate_check.go:39` (changes a sensitive control or state-update path)

Before
```go
predicateArguments := predicateutils.PreparePredicateStorageSlots(rules, tx.AccessList())

	for address, predicates := range predicateArguments {
		// Since [address] is only added to [predicateArguments] when there's a valid predicate in the ruleset
```
After
```go
predicateArguments := predicateutils.PreparePredicateStorageSlots(rules, tx.AccessList())

	// If there are no predicates to verify, return early and skip requiring the proposervm block
	// context to be populated.

	if predicateContext == nil || predicateContext.ProposerVMBlockCtx == nil {
		return nil, ErrMissingPredicateContext
	}
```

## Snippet 3

Context: `core/predicate_check_test.go:111` (changes signature or replay validation logic)

Before
```go
},
			}),
			expectedRes: map[common.Address][]byte{
				addr1: nil,
			},
			expectedErr: nil,
		},
		"predicate named by access list returns non-empty": {
```
After
```go
},
			}),
			expectedErr: ErrMissingPredicateContext,
		},
		"predicate named by access list, without block context errors": {
			gas: 53000,
			predicateContext: &precompileconfig.PredicateContext{
				ProposerVMBlockCtx: nil,
```

## Snippet 4

Context: `core/predicate_check_test.go:78` (changes the branch that decides whether execution stops or continues)

Before
```go
expectedErr: nil,
		},
		"predicate named by access list returns empty": {
			gas: 53000,
			createPredicates: func(t testing.TB) map[common.Address]precompileconfig.Predicater {
				predicate := precompileconfig.NewMockPredicater(gomock.NewController(t))
				arg := common.Hash{1}
				predicate.EXPECT().PredicateGas(arg[:]).Return(uint64(0), nil).Times(2)
```
After
```go
expectedErr: nil,
		},
		"predicate, no access list, no block context passes": {
			gas: 53000,
			predicateContext: &precompileconfig.PredicateContext{
				ProposerVMBlockCtx: nil,
			},
			createPredicates: func(t testing.TB) map[common.Address]precompileconfig.Predicater {
```

# Fix Pattern

Add explicit fail-closed validation for required execution context in the predicate verification path, while preserving early exits for cases that do not require predicate evaluation.

## How It Was Fixed

`core/predicate_check.go` now checks for nil predicate context or nil proposer VM block context and returns `ErrMissingPredicateContext`. `core/predicate_check_test.go` was updated to pass `test.predicateContext`, assert expected errors, and cover missing-context cases.

# Why It Matters

1. Precompile predicate evaluation may depend on block or consensus context.

2. Predicate-named transactions should not be accepted through this path without required context.

3. The patch changes validation from permissive behavior to explicit rejection for missing context.

4. The evidence does not prove a remote exploit or cryptographic bypass.

# Evidence Notes

Grounded evidence comes from `core/predicate_check.go`, where the new guard returns `ErrMissingPredicateContext`, and from `core/predicate_check_test.go`, where the harness now passes per-case context and predicate-named missing-context cases expect the new error. The commit title says missing predicate context should invalidate a block, but the provided evidence only shows `CheckPredicates` returning an error, not the full block invalidation propagation path. Claims about replay, signature bypass, or cryptographic failure are unsupported. Protocol security invariant: Predicate verification should not proceed when a transaction actually requires predicate evaluation but the predicate context or its proposer VM block context is missing. Missing context remains acceptable when there are no predicates to verify. Verification notes: The patch does not prove remote exploitability. The patch does not show how predicateContext becomes nil or loses ProposerVMBlockCtx in production. The patch does not demonstrate a cryptographic failure or signature bypass. The patch preserves acceptance when there are no predicates to verify, so this is not a blanket missing-context rejection. The provided evidence does not show the full block invalidation propagation path beyond CheckPredicates returning an error. Do not classify as confirmed; exploitability is not shown. Do not claim a cryptographic or replay bug from the supplied evidence. Confidence is medium because the patch is clearly validation-related, but the production trigger and full security impact are not established. Keeping in the corpus is reasonable as security hardening because the changed path affects predicate validation and block acceptance semantics. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied patch supports retaining this as security hardening, not a proven security fix. `CheckPredicates` now fails closed with `ErrMissingPredicateContext` when predicate verification is required but `predicateContext` or `ProposerVMBlockCtx` is missing, and tests were updated to expect rejection for predicate-named access-list cases without block context. The evidence does not prove exploitability or the full block invalidation path, but it does show tighter validation in a security-sensitive blockchain predicate/transaction validation path.

## Security Evidence

1. Adds an explicit nil-context guard in `CheckPredicates` returning `ErrMissingPredicateContext`.
2. Tests now pass predicate context per case, allowing missing-context behavior to be exercised directly.
3. Predicate-named access-list cases without block context now expect an error instead of success.
4. Missing context remains allowed when no predicate verification is needed, showing a targeted fail-closed validation change.

## Missing Evidence

1. No proof of a remote exploit or concrete attack path.
2. No evidence showing how production code could supply nil predicate context during block processing.
3. No full propagation evidence proving the returned error invalidates a block end to end.
4. No support for cryptographic bypass, signature bypass, or replay-specific claims.

## Claim Boundaries

1. Classify as security hardening, not confirmed vulnerability remediation.
2. Limit impact to predicate/transaction validation fail-closed behavior.
3. Do not claim exploitability from the supplied patch alone.
4. Do not claim blanket rejection of all missing context; cases with no predicate work still pass.
