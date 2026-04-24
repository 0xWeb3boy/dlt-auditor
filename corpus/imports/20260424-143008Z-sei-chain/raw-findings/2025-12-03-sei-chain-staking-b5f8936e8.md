---
case_id: case_20251203_b5f8936e8
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
source_quality: medium
date: 2025-12-03
source_refs:
  - git:b5f8936e825af5265f2dc3bfd60ce007a39229e6
  - "precompiles/staking/staking_test.go:692"
  - "precompiles/staking/staking_test.go:474"
  - "precompiles/json/json_test.go:282"
  - "precompiles/ibc/ibc_test.go:338"
bug_class: consensus-nondeterminism-hardening
impact_type:
  - consensus-divergence
  - chain-halt
confidence: medium
tags:
  - blockchain-core
  - consensus
  - evm-precompile
  - determinism
  - app-hash
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for consensus nondeterminism in Sei EVM precompile error handling. The provided test evidence shows failed staking, JSON, and IBC precompile paths changing from returning stringified error bytes to returning nil data while still signaling execution failure. The commit body supplies the vulnerability thesis: precompile error strings were placed into return data, bubbled into ABCI result data, and could affect resultsHash/app hash when error text differed across environments.

## Observed Patch Facts

1. In `precompiles/staking/staking_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(res.ReturnData), "Expected error: %s", res.VmE...` with `require.Nil(t, res.ReturnData)`.

2. In `precompiles/staking/staking_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(gotRet))` with `require.Nil(t, gotRet)`.

3. In `precompiles/json/json_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(res))` with `require.Nil(t, res)`.

4. In `precompiles/ibc/ibc_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(gotBz))` with `require.Nil(t, gotBz)`.

## Project Context

The changed code sits primarily in `precompiles/staking`, `precompiles/json`, `precompiles/ibc`, which anchors the finding in the `staking` area of the project. Historical context from `precompiles/staking/staking_events_test.go`, `precompiles/staking/staking.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/staking/staking_events_test.go`, `precompiles/staking/staking.go`. The strongest project-level identifiers around this patch are `require`, `Equal`, `gotRet`, and `VmError`.

## Before/After Behavior

Before the patch, failed precompile tests expected return bytes such as res.ReturnData, gotRet, res, or gotBz to equal tt.wantErrMsg. After the patch, those same failure paths expect nil return data while preserving failure signaling through VmError or vm.ErrExecutionReverted. The inferred intended behavior is that failed precompiles no longer return serialized diagnostic error strings in consensus-relevant result data.

# Root Cause

The commit body identifies the root cause as shared precompile error handling populating return data with the stringified error on failure. Because the commit body states ABCI resultsHash includes the transaction result data field, nondeterministic error strings, including potentially environment-specific stack or executable-path details, could become consensus-marshalled data.

## Walkthrough

1. A shared precompile execution path returns an error.

2. Before the fix, the error string was exposed as return data according to the commit body and reflected by tests that compared returned bytes to tt.wantErrMsg.

3. ABCI transaction result data is described in the commit body as part of the marshalled result used for resultsHash/app hash.

4. If the stringified error differed across nodes, the result data could differ for the same failed precompile execution.

5. The patch changes expected failed precompile behavior so return data is nil.

6. Failure is still observable through execution error channels such as VmError or vm.ErrExecutionReverted.

7. Updated tests cover staking, JSON, and IBC precompile failure cases asserting nil return data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/common/precompiles.go | 159 | shared precompile error handling path that previously populated return data with stringified errors and is the main fix location described by the commit |
| precompiles/staking/staking_test.go | 474 | staking precompile Run error test now asserts vm.ErrExecutionReverted with nil return data |
| precompiles/staking/staking_test.go | 692 | EVM transaction staking create-validator error test now asserts nil res.ReturnData instead of a specific error string |
| precompiles/json/json_test.go | 282 | json precompile error test now asserts nil result bytes instead of serialized error text |
| precompiles/ibc/ibc_test.go | 338 | ibc precompile error test now asserts nil return bytes on reverted execution |

## Code Snippets

## Snippet 1

Context: `precompiles/staking/staking_test.go:692` (changes a sensitive control or state-update path)

Before
```go
if tt.wantErr {
				require.NotEmpty(t, res.VmError, "Expected error but transaction succeeded")
				require.Equal(t, tt.wantErrMsg, string(res.ReturnData), "Expected error: %s", res.VmError)
			} else {
				require.Empty(t, res.VmError, "Unexpected error: %s", res.VmError)
```
After
```go
if tt.wantErr {
				require.NotEmpty(t, res.VmError, "Expected error but transaction succeeded")
				require.Nil(t, res.ReturnData)
			} else {
				require.Empty(t, res.VmError, "Unexpected error: %s", res.VmError)
```

## Snippet 2

Context: `precompiles/staking/staking_test.go:474` (changes a sensitive control or state-update path)

Before
```go
if err != nil {
				require.Equal(t, vm.ErrExecutionReverted, err)
				require.Equal(t, tt.wantErrMsg, string(gotRet))
			} else if !reflect.DeepEqual(gotRet, tt.wantRet) {
				t.Errorf("Run() gotRet = %v, want %v", gotRet, tt.wantRet)
```
After
```go
if err != nil {
				require.Equal(t, vm.ErrExecutionReverted, err)
				require.Nil(t, gotRet)
			} else if !reflect.DeepEqual(gotRet, tt.wantRet) {
				t.Errorf("Run() gotRet = %v, want %v", gotRet, tt.wantRet)
```

## Snippet 3

Context: `precompiles/json/json_test.go:282` (changes a sensitive control or state-update path)

Before
```go
if tt.wantErr {
				require.Error(t, err)
				require.Equal(t, tt.wantErrMsg, string(res))
				return
			} else {
```
After
```go
if tt.wantErr {
				require.Error(t, err)
				require.Nil(t, res)
				return
			} else {
```

## Snippet 4

Context: `precompiles/ibc/ibc_test.go:338` (changes a sensitive control or state-update path)

Before
```go
if err != nil {
				require.Equal(t, vm.ErrExecutionReverted, err)
				require.Equal(t, tt.wantErrMsg, string(gotBz))
			} else if !reflect.DeepEqual(gotBz, tt.wantBz) {
				t.Errorf("Run() gotRet = %v, want %v", gotBz, tt.wantBz)
```
After
```go
if err != nil {
				require.Equal(t, vm.ErrExecutionReverted, err)
				require.Nil(t, gotBz)
			} else if !reflect.DeepEqual(gotBz, tt.wantBz) {
				t.Errorf("Run() gotRet = %v, want %v", gotBz, tt.wantBz)
```

# Fix Pattern

Keep nondeterministic diagnostics out of consensus-relevant serialized fields. Signal precompile failure through deterministic error handling while returning nil bytes instead of stringified error text on failed execution.

## How It Was Fixed

The commit body says the implementation change is in precompiles/common/precompiles.go, where failed precompile execution no longer populates return data with the stringified error. The supplied direct evidence is test updates in precompiles/staking/staking_test.go, precompiles/json/json_test.go, and precompiles/ibc/ibc_test.go that replace exact error-message return-byte expectations with nil return-data assertions.

# Why It Matters

1. Consensus result hashes must be identical across nodes.

2. Error strings can vary by environment, wrapping, or stack details.

3. Including nondeterministic return data in app-hash inputs can cause validator divergence or chain halt.

4. The evidence does not show theft, authorization bypass, or state-transition side effects.

# Evidence Notes

Downgraded from confirmed/high to likely/medium because the supplied diff evidence primarily shows test expectation changes; the implementation hunk in precompiles/common/precompiles.go is referenced by the commit body but not directly included. The consensus nondeterminism thesis is still reasonably grounded by the detailed commit body and by tests across multiple precompile subsystems changing failed-call return data from error strings to nil. The issue is not a staking-specific authorization bug; staking is one affected caller of shared precompile error behavior. Protocol security invariant: Consensus-marshalled transaction result fields, including ABCI result data used in resultsHash/app hash, must be deterministic across nodes. Failed EVM precompile execution must not put environment-dependent or wrapping-dependent error text into return data that can be included in consensus results. Verification notes: The patch does not prove a remote exploit path or attacker-controlled validator divergence trigger beyond the described nondeterministic error data mechanism. The evidence does not show incorrect staking authorization, balance theft, or state transition side effects. The tests shown are mostly expectation updates; the exact implementation diff in precompiles/common/precompiles.go is described by commit context but not included as a hunk. The commit author states this should not be treated as increasing security by preserving error-message consensus checks; the mapped issue is determinism of consensus-marshalled data. Direct evidence: staking tests now assert nil res.ReturnData or gotRet on error. Direct evidence: JSON and IBC precompile tests now assert nil result bytes on error. Commit-body evidence: resultsHash/app hash includes marshalled transaction result data. Commit-body evidence: precompile errors previously populated return data with stringified errors. Implementation behavior is not directly quoted in the supplied hunks, so confirmation depends partly on commit-message context. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-nondeterminism-hardening`
Final impact type: `consensus-divergence, chain-halt`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, evm-precompile, determinism, app-hash`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The commit body gives a concrete consensus-safety mechanism: nondeterministic precompile error strings were included in return data that could flow into ABCI transaction result data and affect resultsHash/app hash. The supplied patch evidence shows multiple failed precompile paths changing from returning exact error strings to nil return data while preserving execution failure. However, the direct implementation hunk is not supplied, and the commit itself notes no concrete security exploit, so the corpus entry should avoid claiming a proven exploitable vulnerability.

## Security Evidence

1. Commit body states different precompile error messages can lead to app hash differences.
2. Commit body states resultsHash is derived from marshalled transaction results and only deterministic fields should be included.
3. Commit body identifies the data field as nondeterministic because it was populated with stringified precompile errors.
4. Tests across staking, JSON, and IBC now assert nil return data on failed precompile execution instead of serialized error text.
5. Failure signaling remains through VmError or vm.ErrExecutionReverted, reducing consensus-visible diagnostic data.

## Missing Evidence

1. No direct implementation diff from precompiles/common/precompiles.go is included in the supplied evidence.
2. No reproduction output demonstrating validator divergence or app hash mismatch is included.
3. No attacker-controlled exploit path or concrete chain halt scenario is proven by the patch alone.
4. The commit body includes an author comment that frames the change as not directly affecting security.

## Claim Boundaries

1. Classify as consensus determinism hardening, not theft, authorization bypass, or staking-specific access control.
2. Do not claim confirmed exploitation or a remotely triggerable vulnerability from the supplied evidence alone.
3. Do not treat the issue as limited to staking; staking is one tested caller of shared precompile error behavior.
4. The supported impact is potential consensus divergence or app hash break, not direct state corruption or fund loss.
