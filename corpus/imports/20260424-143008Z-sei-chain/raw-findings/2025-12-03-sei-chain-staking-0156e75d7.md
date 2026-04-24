---
case_id: case_20251203_0156e75d7
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
  - git:0156e75d77da795538af71e84a80bc4c443d7ca8
  - "precompiles/staking/staking_test.go:692"
  - "precompiles/staking/staking_test.go:474"
  - "precompiles/json/json_test.go:282"
  - "precompiles/ibc/ibc_test.go:338"
bug_class: consensus-determinism-hardening
impact_type:
  - consensus-safety
  - chain-liveness
confidence: medium
tags:
  - blockchain-core
  - evm-precompiles
  - consensus-determinism
  - app-hash
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for consensus nondeterminism in EVM precompile error handling. The provided evidence shows failed precompile calls previously returned stringified error bytes and now return nil data while still reporting execution failure. The commit context states that this return data can bubble into the ABCI data field included in consensus resultsHash/app hash, and that stringified errors can vary across nodes.

## Observed Patch Facts

1. In `precompiles/staking/staking_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(res.ReturnData), "Expected error: %s", res.VmE...` with `require.Nil(t, res.ReturnData)`.

2. In `precompiles/staking/staking_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(gotRet))` with `require.Nil(t, gotRet)`.

3. In `precompiles/json/json_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(res))` with `require.Nil(t, res)`.

4. In `precompiles/ibc/ibc_test.go`, the patch replaces `require.Equal(t, tt.wantErrMsg, string(gotBz))` with `require.Nil(t, gotBz)`.

## Project Context

The changed code sits primarily in `precompiles/staking`, `precompiles/json`, `precompiles/ibc`, which anchors the finding in the `staking` area of the project. Historical context from `precompiles/staking/staking_events_test.go`, `precompiles/staking/staking.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/staking/staking_events_test.go`, `precompiles/staking/staking.go`. The strongest project-level identifiers around this patch are `require`, `Equal`, `gotRet`, and `VmError`.

## Before/After Behavior

Before the patch, failed precompile executions were expected to preserve error text in returned bytes, with tests comparing ReturnData, gotRet, res, or gotBz against tt.wantErrMsg. After the patch, those same failure paths still expect an error such as vm.ErrExecutionReverted or a non-empty VmError, but assert nil return data. The behavior change is limited to removing stringified error bytes from failed precompile return data, not changing the fact that execution failed.

# Root Cause

Precompile failure handling copied stringified errors into return data. According to the commit context, that return data can become ABCI transaction result data, which is included in the marshalled result used for consensus hashing. Since error strings may contain nondeterministic node-local content such as executable paths or call stack details, including them could violate consensus determinism.

## Walkthrough

1. A precompile call fails during execution in a path such as staking, JSON, or IBC.

2. The prior behavior converted the failure into an execution-reverted error while also returning the underlying error string as bytes.

3. Tests before the patch explicitly expected those bytes to equal tt.wantErrMsg.

4. The commit context states that returned bytes can flow into ABCI transaction result data.

5. The commit context also states that the ABCI data field contributes to consensus resultsHash/app hash.

6. If the stringified error differs across validators, the consensus-hashed transaction result can differ.

7. The patch changes failed precompile calls to keep failure signaling through the error path while returning nil data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/common/precompiles.go | 159 | common precompile error handling path that previously populated return data with stringified errors on failure |
| precompiles/staking/staking_test.go | 474 | staking precompile Run error case now asserts nil return data instead of an error string |
| precompiles/staking/staking_test.go | 692 | EVM transaction staking failure path now asserts nil ReturnData when VmError is present |
| precompiles/json/json_test.go | 282 | JSON precompile failure path now asserts nil result bytes instead of stringified error output |
| precompiles/ibc/ibc_test.go | 338 | IBC precompile failure path now asserts nil return bytes on execution revert |

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

Do not place raw or stringified error messages into consensus-visible return data on failed precompile execution. Preserve failure signaling through the VM error path and leave return data nil for errored precompile calls.

## How It Was Fixed

The common precompile error behavior was changed so errored precompile runs do not populate return data with the error string. Tests across staking, JSON, and IBC were updated to assert nil returned bytes whenever an error is expected while still checking that the error path is taken.

# Why It Matters

1. Protects consensus-hashed transaction result fields from nondeterministic error strings.

2. Prevents node-local error formatting differences from entering ABCI data through precompile ReturnData.

3. Keeps the finding scoped to consensus determinism, not theft, privilege escalation, or staking authorization.

4. Avoids treating helper or test changes as the root cause.

# Evidence Notes

Primary evidence is the before/after test behavior: staking Run errors changed from comparing string(gotRet) to requiring nil gotRet; staking EVM transaction failures changed from comparing string(res.ReturnData) to requiring nil ReturnData; JSON failures changed from comparing string(res) to requiring nil res; and IBC failures changed from comparing string(gotBz) to requiring nil gotBz. The commit message supplies the consensus mechanism and identifies precompiles/common/precompiles.go as the error handling path. The supplied evidence does not prove a concrete remote exploit path, theft, privilege escalation, direct state corruption, full side-effect freedom of all precompile errors, or sensitive secret exposure beyond possible local paths or call stacks. Protocol security invariant: Fields included in consensus resultsHash/app hash must be deterministic across validators. Failed EVM precompile execution must not place node-local or otherwise variable stringified error data into ReturnData/ABCI data when that data is part of the marshalled transaction result. Verification notes: The patch does not prove a concrete remote exploit path or adversarial triggerability. The patch does not show theft, privilege escalation, or direct state corruption. The patch does not prove all precompile errors are side-effect free; the commit notes this as needing confirmation. The evidence supports consensus nondeterminism/app-hash risk, not a staking-specific business-logic vulnerability. The patch removes error return data visibility but does not establish that the error messages themselves exposed sensitive secrets beyond possible local paths or call stacks. Tests were updated to assert nil return data on expected precompile errors. Commit message says a local chain was run against the reproduction suite. Commit message says CI/CD was run. No independent command output or full implementation diff is provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-determinism-hardening`
Final impact type: `consensus-safety, chain-liveness`
Final confidence: `medium`
Final tags: `blockchain-core, evm-precompiles, consensus-determinism, app-hash, security-hardening`

The evidence supports retaining this as security hardening, not a proven security fix. The commit context explains that failed precompile return data could include nondeterministic stringified errors and flow into ABCI transaction result data used for consensus resultsHash/app hash. The patch evidence shows tests changed to require nil return data on precompile errors across staking, JSON, and IBC paths. That tightens a consensus-sensitive behavior, but the supplied evidence does not prove a concrete exploit path, adversarial triggerability, or an actual observed consensus failure.

## Security Evidence

1. Commit states resultsHash/app hash is derived from marshalled transaction results and only deterministic fields should be included.
2. Commit states precompile error return data populated with stringified errors can bubble into the consensus-included ABCI data field.
3. Commit states stringified errors can contain nondeterministic local details such as executable paths or call stack data.
4. Tests now expect nil return data for errored precompile calls instead of expecting specific error-message bytes.
5. The affected behavior is in blockchain EVM precompile execution, a consensus-sensitive subsystem.

## Missing Evidence

1. No implementation diff for precompiles/common/precompiles.go is included, only test evidence and commit explanation.
2. No concrete remote exploit or adversarial transaction sequence is shown.
3. No proof is supplied that the nondeterminism was reachable on production validators under realistic conditions.
4. No evidence of theft, privilege escalation, authorization bypass, or direct state corruption.
5. Commit text itself says the change should not affect security, framing the issue more as consensus correctness/hardening.

## Claim Boundaries

1. Classify as consensus determinism hardening rather than a confirmed exploitable vulnerability.
2. Do not claim staking-specific authorization impact; staking is only one tested precompile area.
3. Do not claim sensitive secret disclosure beyond possible local paths or call stack details mentioned in the commit.
4. Do not claim all precompile error paths are side-effect free; the commit says that needed confirmation.
5. Do not upgrade to security-fix without implementation evidence and a demonstrated security impact path.
