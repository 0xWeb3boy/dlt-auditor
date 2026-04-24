---
case_id: case_20240407_ac07554f71
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-04-07
source_refs:
  - git:ac07554f71c901ff7b37eeb5e8c9a0acb00297cf
  - "precompiles/ArbWasmCache.go:88"
  - "precompiles/ArbWasmCache.go:68"
  - "arbos/programs/programs.go:333"
  - "precompiles/ArbWasmCache.go:37"
bug_class: access-control-error-handling
impact_type:
  - privileged-operation-access-control
confidence: medium
tags:
  - blockchain-core
  - precompile
  - access-control
  - authorization
  - error-handling
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects an authorization predicate in `ArbWasmCache.hasAccess` by changing the chain-owner branch from `owner && err != nil` to `owner && err == nil`. This is security-relevant access-control code, but the supplied evidence does not establish an exploitable vulnerability because the behavior of `IsMember` on error is not shown and no unauthorized access path is proven.

## Observed Patch Facts

1. In `precompiles/ArbWasmCache.go`, the patch replaces `return owner && err != nil` with `return owner && err == nil`.

2. In `precompiles/ArbWasmCache.go`, the patch replaces `// Reads the trie table record at the given offset. Caller must be a cache manager or...` with `func (con ArbWasmCache) setProgramCached(c ctx, evm mech, codehash hash, cached bool)...`.

3. In `arbos/programs/programs.go`, the patch replaces `// Sets whether a program is cached. Errors if the program is expired.` with `// Sets whether a program is cached. Errors if trying to cache an expired program.`.

4. In `precompiles/ArbWasmCache.go`, the patch replaces `// Caches all programs with the given codehash. Caller must be a cache manager or cha...` with `// Reads the trie table record at the given offset. Caller must be a cache manager or...`.

## Project Context

The changed code sits primarily in `arbos/programs`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `precompiles/ArbWasm.go`, `precompiles/ArbOwner.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbos/programs/wasm.go`, `arbos/programs/native.go`. The strongest project-level identifiers around this patch are `error`, `cached`, `uint64`, and `addr`.

## Before/After Behavior

Before the patch, cache-manager callers were allowed only after a successful cache-manager membership check, but chain-owner callers were allowed only when `owner` was true and the chain-owner lookup returned an error. A normal successful chain-owner lookup with `err == nil` would not pass. After the patch, chain-owner access requires `owner` with `err == nil`. Guarded paths such as `setProgramCached` and `SetTrieTableParams` continue to call `hasAccess` before mutating cache-related state. The `Programs.SetProgramCached` changes adjust cache-state handling for expired programs, but the provided evidence does not establish a separate security issue there.

# Root Cause

An inverted error check in the chain-owner branch of `ArbWasmCache.hasAccess`: the code required a non-nil error instead of a nil error for successful chain-owner authorization.

## Walkthrough

1. `ArbWasmCache.hasAccess` first checks whether the caller is a cache manager.

2. If the cache-manager lookup errors, access is denied.

3. If the caller is a cache manager, access is granted.

4. For non-cache-manager callers, the function checks chain-owner membership.

5. Before the patch, the chain-owner branch returned `owner && err != nil`.

6. After the patch, the chain-owner branch returns `owner && err == nil`.

7. State-changing ArbWasmCache paths such as `setProgramCached` and `SetTrieTableParams` are guarded by this predicate.

8. The evidence does not show whether `IsMember` can return `owner == true` with an error for an unauthorized caller.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/ArbWasmCache.go | 81 | authorization gate for ArbWasmCache privileged methods, checking cache-manager or chain-owner membership |
| precompiles/ArbWasmCache.go | 66 | privileged setProgramCached path guarded by hasAccess before mutating program cache state |
| precompiles/ArbWasmCache.go | 26 | privileged SetTrieTableParams path guarded by hasAccess before changing cache trie parameters |
| arbos/programs/programs.go | 330 | program cache-state storage logic used by ArbWasmCache cache and evict operations |

## Code Snippets

## Snippet 1

Context: `precompiles/ArbWasmCache.go:88` (changes an authorization or privilege gate)

Before
```go
}
	owner, err := c.State.ChainOwners().IsMember(c.caller)
	return owner && err != nil
}

func (con ArbWasmCache) setProgramCached(c ctx, evm mech, codehash hash, cached bool) error {
	if !con.hasAccess(c) {
		return c.BurnOut()
```
After
```go
}
	owner, err := c.State.ChainOwners().IsMember(c.caller)
	return owner && err == nil
}
```

## Snippet 2

Context: `precompiles/ArbWasmCache.go:68` (changes signature or replay validation logic)

Before
```go
}

// Reads the trie table record at the given offset. Caller must be a cache manager or chain owner.
func (con ArbWasmCache) ReadTrieTableRecord(c ctx, evm mech, offset uint64) (huge, addr, uint64, error) {
	if !con.hasAccess(c) {
		return nil, addr{}, 0, c.BurnOut()
	}
	return nil, addr{}, 0, errors.New("unimplemented")
```
After
```go
}

func (con ArbWasmCache) setProgramCached(c ctx, evm mech, codehash hash, cached bool) error {
	if !con.hasAccess(c) {
		return c.BurnOut()
	}
	params, err := c.State.Programs().Params()
	if err != nil {
```

## Snippet 3

Context: `arbos/programs/programs.go:333` (changes signature or replay validation logic)

Before
```go
}

// Sets whether a program is cached. Errors if the program is expired.
func (p Programs) SetProgramCached(codeHash common.Hash, cached bool, time uint64, params *StylusParams) error {
	program, err := p.getProgram(codeHash, time, params)
	if err != nil {
		return err
	}
```
After
```go
}

// Sets whether a program is cached. Errors if trying to cache an expired program.
func (p Programs) SetProgramCached(codeHash common.Hash, cache bool, time uint64, params *StylusParams) error {
	data, err := p.programs.Get(codeHash)
	if err != nil {
		return err
	}
```

## Snippet 4

Context: `precompiles/ArbWasmCache.go:37` (changes a sensitive control or state-update path)

Before
```go
}

// Caches all programs with the given codehash. Caller must be a cache manager or chain owner.
func (con ArbWasmCache) CacheCodehash(c ctx, evm mech, codehash hash) error {
```
After
```go
}

// Reads the trie table record at the given offset. Caller must be a cache manager or chain owner.
func (con ArbWasmCache) ReadTrieTableRecord(c ctx, evm mech, offset uint64) (huge, addr, uint64, error) {
	if !con.hasAccess(c) {
		return nil, addr{}, 0, c.BurnOut()
	}
	return nil, addr{}, 0, errors.New("unimplemented")
```

# Fix Pattern

Correct an authorization condition so successful membership requires a positive membership result and no lookup error.

## How It Was Fixed

The patch changed `precompiles/ArbWasmCache.go` so the chain-owner branch of `hasAccess` accepts `owner && err == nil` instead of `owner && err != nil`. It also adjusted `Programs.SetProgramCached` cache-state handling, but that part is only shown as related support logic in the provided evidence.

# Why It Matters

1. The changed code is an authorization gate for privileged cache-management operations.

2. The previous condition contradicted the documented cache-manager-or-chain-owner access rule.

3. The evidence supports an access-control correctness issue, but not a proven privilege escalation.

4. Unimplemented trie table methods do not establish practical impact.

# Evidence Notes

The strongest evidence is the one-line change in `precompiles/ArbWasmCache.go` inside `hasAccess`. The claim that normal chain owners were incorrectly denied is supported by the visible predicate. The claim that unauthorized callers could gain access is not supported because `IsMember` error semantics are not provided. The `ReadTrieTableRecord` and `WriteTrieTableRecord` snippets are unimplemented, so they should not be treated as impact evidence. The `Programs.SetProgramCached` changes are related cache-state logic, but no separate vulnerability thesis is established from the supplied snippets. Protocol security invariant: ArbWasmCache administrative operations should only proceed when the caller is an authorized cache manager or chain owner and the relevant membership lookup succeeds; membership lookup errors should not be treated as successful authorization. Verification notes: The patch does not prove that an unauthorized external caller could gain access before the fix. The patch does not prove loss of funds, consensus failure, or arbitrary state corruption. The patch may primarily restore intended chain-owner administration rather than fix an exploitable privilege escalation. ReadTrieTableRecord and WriteTrieTableRecord are shown as unimplemented, so their practical security impact is not established by this evidence. The exact behavior of IsMember on error is not provided, so allow-on-error exploitability is not proven. No exploit path is demonstrated by the provided evidence. No loss of funds, consensus failure, or arbitrary state corruption is shown. Security relevance is plausible because the predicate guards privileged precompile methods. Keep out of the security corpus unless additional evidence shows unauthorized access or concrete impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `access-control-error-handling`
Final impact type: `privileged-operation-access-control`
Final confidence: `medium`
Final tags: `blockchain-core, precompile, access-control, authorization, error-handling, security-hardening`

The evidence supports retaining this as security hardening, not a proven exploitable security fix. The patch changes an authorization predicate for ArbWasmCache privileged operations so chain-owner access requires a successful membership lookup (`err == nil`) instead of a failed one (`err != nil`). That clearly tightens security-sensitive access-control behavior, but the supplied evidence does not prove that an unauthorized caller could actually obtain access or that `IsMember` can return `owner == true` with an error.

## Security Evidence

1. `ArbWasmCache.hasAccess` gates privileged cache-related operations.
2. The chain-owner authorization branch changed from `owner && err != nil` to `owner && err == nil`.
3. The fixed condition requires both positive membership and no lookup error before granting chain-owner access.
4. Callers failing `hasAccess` are rejected with `BurnOut()` on guarded paths such as `setProgramCached`.

## Missing Evidence

1. No semantics are shown for `ChainOwners().IsMember` when it returns an error.
2. No proof that an unauthorized caller could produce `owner == true` with `err != nil`.
3. No demonstrated exploit path, loss of funds, consensus failure, or arbitrary state corruption.
4. The unimplemented trie-table methods do not establish practical impact.

## Claim Boundaries

1. Treat as access-control hardening rather than confirmed privilege escalation.
2. Do not claim concrete exploitability from the provided patch alone.
3. Do not infer impact from unrelated cache-state refactoring or unimplemented methods.
4. Supported claim is limited to correcting error handling in a privileged authorization gate.
