---
case_id: case_20260407_b4cd4e850
project: nitro
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2026-04-07
source_refs:
  - git:b4cd4e850d3ca3332a6fc68f52cb03aa2e68d4c2
  - "arbos/programs/testcompile.go:495"
  - "arbos/programs/testcompile.go:663"
  - "arbos/programs/native.go:612"
  - "arbos/programs/native.go:628"
bug_class: resource-exhaustion-guard
impact_type:
  - availability
confidence: medium
tags:
  - blockchain-core
  - wasm
  - native-execution
  - stack-overflow
  - resource-limits
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best supported as runtime hardening for native stack-overflow handling, not as a demonstrated security fix. The shown changes bound stack-growth retry behavior and update tests around that path, but the provided evidence does not establish an exploitable vulnerability or a protocol-level security violation.

## Observed Patch Facts

1. In `arbos/programs/testcompile.go`, the patch replaces `SetInitialNativeStackSize(32 * 1024)` with `wasm, err := Wat2Wasm(recursiveStackOverflowWat)`.

2. In `arbos/programs/testcompile.go`, the patch replaces `// Compile cranelift ASM so the retry path succeeds.` with `localAsm, err := compileNative(wasm, 1, true, localTarget, false, time.Minute)`.

3. In `arbos/programs/native.go`, the patch replaces `log.Warn("native stack overflow, no retry for off-chain execution",` with `log.Warn("native stack overflow, no stack doubling for off-chain execution",`.

4. In `arbos/programs/native.go`, the patch replaces `log.Error("native stack overflow at max stack size, giving up",` with `log.Error("native stack overflow at max stack size, cannot double further",`.

## Project Context

The changed code sits primarily in `arbos/programs`, which anchors the finding in the `storage` area of the project. Historical context from `arbos/programs/cgo_test.go`, `arbos/programs/programs.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbos/programs/cgo_test.go`, `arbos/programs/programs.go`. The strongest project-level identifiers around this patch are `stack`, `native`, `cranelift`, and `overflow`.

## Before/After Behavior

Before the change, the overflow handler already returned for off-chain execution, but it did not show the new one-time `hasDoubledNativeStack` guard and used older retry-related logging. After the change, off-chain execution still returns immediately, on-chain handling refuses to double the stack more than once, logs when no further doubling is possible, marks that doubling has occurred, and retries through the cranelift-oriented path. The tests were rewritten to compile a recursive overflow wasm case and both native/cranelift assemblies instead of relying only on direct stack-size setup.

# Root Cause

The evidence supports an insufficiently bounded recovery path after native stack overflow. The handler needed an explicit one-time guard and clearer limits around stack growth and retry selection.

## Walkthrough

1. In `arbos/programs/native.go`, the off-chain branch changes its log from `no retry for off-chain execution` to `no stack doubling for off-chain execution` but still returns `userNativeStackOverflow`, so the evidence does not support any claim that off-chain execution previously continued into retry logic.

2. The same handler now checks `hasDoubledNativeStack.Load()` and returns without doubling again, adding an explicit one-time guard.

3. The max-size path now logs `cannot double further` and returns when doubling would not increase the stack size, making the bound explicit.

4. The retry path logs `doubling stack size and retrying with cranelift` and stores `hasDoubledNativeStack` as true before retry selection.

5. Comments in the changed hunk state cranelift is more stack-efficient and is preferred for the retry, with fallback to the original assembly if cranelift output is unavailable.

6. `arbos/programs/testcompile.go` changes the tests to build a recursive stack-overflow wasm input and precompile both local native and cranelift assemblies, which directly exercises the overflow-handling path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbos/programs/native.go | 588 | primary overflow handler for native Stylus execution; adds one-time stack-doubling guard and off-chain restriction |
| arbos/programs/native.go | 628 | bounded stack growth and retry selection logic for cranelift fallback |
| arbos/programs/testcompile.go | 491 | unit/integration test for native stack overflow handling path |
| arbos/programs/testcompile.go | 654 | test for retry behavior and restoration of execution pages/state |

## Code Snippets

## Snippet 1

Context: `arbos/programs/testcompile.go:495` (changes persisted or aggregate state handling)

Before
```go
}

	SetInitialNativeStackSize(32 * 1024)
	DrainStackPool()

	gas := uint64(0xfffffffffffffff)
	evm, scope, db := makeTestEVMScope(gas)
	scope.Contract.Gas = gas
```
After
```go
}

	wasm, err := Wat2Wasm(recursiveStackOverflowWat)
	if err != nil {
		return fmt.Errorf("failed compiling WAT: %w", err)
	}

	localAsm, err := compileNative(wasm, 1, true, localTarget, false, time.Minute)
```

## Snippet 2

Context: `arbos/programs/testcompile.go:663` (changes a sensitive control or state-update path)

Before
```go
}

	// Compile cranelift ASM so the retry path succeeds.
	craneliftAsm, err := compileNative(wasm, 1, true, localTarget, true, time.Minute)
	if err != nil {
```
After
```go
}

	localAsm, err := compileNative(wasm, 1, true, localTarget, false, time.Minute)
	if err != nil {
		return fmt.Errorf("failed compiling native: %w", err)
	}

	// Compile cranelift ASM for the retry.
```

## Snippet 3

Context: `arbos/programs/native.go:612` (changes bounds, limits, or capacity handling)

Before
```go
}
	if !runCtx.IsExecutedOnChain() {
		log.Warn("native stack overflow, no retry for off-chain execution",
			"program", address, "module", moduleHash)
		return userNativeStackOverflow, nil
	}

	// Get or compile cranelift ASM (persisted to wasm store on compilation).
```
After
```go
}
	if !runCtx.IsExecutedOnChain() {
		log.Warn("native stack overflow, no stack doubling for off-chain execution",
			"program", address, "module", moduleHash)
		return userNativeStackOverflow, nil
	}
	if hasDoubledNativeStack.Load() {
		log.Warn("native stack overflow after stack was already doubled, not doubling again",
```

## Snippet 4

Context: `arbos/programs/native.go:628` (changes bounds, limits, or capacity handling)

Before
```go
}
	if newStackSize <= baseStackSize {
		log.Error("native stack overflow at max stack size, giving up",
			"program", address, "module", moduleHash, "stackSize", baseStackSize)
		return userNativeStackOverflow, nil
	}

	log.Warn("native stack overflow with cranelift, doubling stack size",
```
After
```go
}
	if newStackSize <= baseStackSize {
		log.Error("native stack overflow at max stack size, cannot double further",
			"program", address, "module", moduleHash, "stackSize", baseStackSize)
		return userNativeStackOverflow, nil
	}

	log.Warn("native stack overflow, doubling stack size and retrying with cranelift",
```

# Fix Pattern

Add an explicit one-time guard to a recovery path, cap resource growth, restrict the behavior by execution context, and add tests that exercise the bounded retry flow.

## How It Was Fixed

The handler now prevents repeated stack doubling with `hasDoubledNativeStack`, refuses doubling when the configured stack cannot grow further, keeps off-chain execution on the immediate failure path, and performs at most one retry after increasing stack size. The tests were updated to construct an actual recursive overflow case and cover both native and cranelift code paths.

# Why It Matters

1. Prevents repeated stack-growth attempts in the overflow-recovery path.

2. Makes the retry behavior explicitly bounded.

3. Separates off-chain handling from on-chain recovery behavior.

4. Improves test coverage for the overflow path.

# Evidence Notes

The draft overstated some behavior. In the provided before/after snippet, the off-chain branch already returned immediately before the patch, so there is no support for claiming it previously proceeded into retry logic. The supplied evidence supports a resource-control and runtime-hardening interpretation, but not storage corruption, privilege bypass, data exposure, consensus failure, or a clearly exploitable denial-of-service claim. Protocol security invariant: The evidence supports only a narrow runtime invariant: when native Stylus execution hits a native stack overflow during on-chain execution, the handler may double the native stack at most once and then retry, while off-chain execution must not trigger stack doubling. Verification notes: The patch does not prove attacker-controlled code can reliably trigger a consensus failure or node compromise. The patch does not show a privilege bypass, authentication flaw, or data exposure issue. The patch does not establish whether repeated stack doubling was reachable from untrusted on-chain inputs in practice. The patch suggests availability hardening, but not a demonstrated exploitable denial-of-service vulnerability. Assessment is based only on the provided commit metadata and code excerpts. No full diff, runtime trace, or exploit demonstration was provided. The updated tests support intended behavior changes, but they do not by themselves establish security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion-guard`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `blockchain-core, wasm, native-execution, stack-overflow, resource-limits`

The patch evidence supports retaining this as a security-hardening case, not as a proven exploitable security fix. The changed handler is in an on-chain native execution path, and it clearly tightens a resource-sensitive overflow recovery mechanism by allowing stack growth at most once, refusing further growth at the limit, and keeping off-chain execution on the fail-fast path. That is relevant hardening for availability and runtime safety, but the supplied diff does not prove prior exploitability, state corruption, or a concrete consensus/security break.

## Security Evidence

1. The on-chain overflow handler adds a one-time `hasDoubledNativeStack` guard before any further stack growth.
2. The handler explicitly caps stack growth and returns when no larger stack can be allocated.
3. The code distinguishes off-chain execution and refuses stack doubling there, preserving a stricter fail-fast path.
4. The retry path is narrowed to a bounded fallback flow and accompanied by focused regression tests for recursive overflow behavior.

## Missing Evidence

1. No proof that untrusted inputs could previously trigger repeated stack growth in production.
2. No evidence of prior state corruption, privilege bypass, or data exposure.
3. No exploit, crash loop, consensus-failure trace, or demonstrated denial-of-service impact is shown.
4. Only partial diff context is provided, so full before/after control flow is not proven.

## Claim Boundaries

1. Supported claim: this hardens native stack-overflow handling in a security-sensitive execution path.
2. Supported claim: the patch reduces risk of uncontrolled or repeated retry/stack-growth behavior.
3. Not supported: storage corruption or database/snapshot integrity impact.
4. Not supported: a confirmed exploitable vulnerability or protocol-level break.
