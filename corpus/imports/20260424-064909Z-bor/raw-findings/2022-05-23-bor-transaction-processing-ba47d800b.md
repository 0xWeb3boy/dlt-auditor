---
case_id: case_20220523_ba47d800b
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2022-05-23
source_refs:
  - git:ba47d800b13058885288c38bd174babb38560c89
  - "eth/tracers/js/tracer_test.go:275"
  - "eth/tracers/js/goja.go:603"
  - "eth/tracers/js/goja.go:452"
  - "eth/tracers/js/goja.go:688"
bug_class: panic-on-invalid-input
impact_type:
  - availability
confidence: medium
tags:
  - rpc
  - tracing
  - js-engine
  - panic-handling
  - input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidenced change is in the Goja-based tracing runtime under eth/tracers/js, where several helper paths stop using panic-driven failure handling and instead interrupt the VM and return nil. This is a real robustness improvement, but the provided evidence does not establish an exploitable vulnerability or even that these panic paths could crash a node in deployment.

## Observed Patch Facts

1. In `eth/tracers/js/tracer_test.go`, the patch removes `// Tests too deep object / serialization crash for duktape`.

2. In `eth/tracers/js/goja.go`, the patch replaces `value := s.w.peek(idx)` with `value, err := s.peek(idx)`.

3. In `eth/tracers/js/goja.go`, the patch replaces `panic(err)` with `vm.Interrupt(err)`.

4. In `eth/tracers/js/goja.go`, the patch replaces `panic(err)` with `do.vm.Interrupt(err)`.

## Project Context

The changed code sits primarily in `eth/tracers/js`, `eth/tracers`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/tracers/js/bigint.go`, `eth/tracers/api.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/tracers/api.go`, `eth/tracers/js/bigint.go`. The strongest project-level identifiers around this patch are `start`, `Interrupt`, `panic`, and `function`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/calltrace_test.go`.

## Before/After Behavior

Before the patch, several tracer-exposed Go helpers used panic(err) on decode/conversion failures, and memory.slice only logged an out-of-bounds access before continuing. After the patch, those paths call vm.Interrupt(...) and return nil, so invalid tracer inputs and illegal slice ranges terminate tracing in-band instead of following panic or warn-and-continue behavior.

# Root Cause

The Goja tracer host helpers handled invalid inputs and helper failures with raw Go panics, and one memory slicing path treated bounds violations as a warning instead of an immediate failure.

## Walkthrough

1. The commit message says native Go functions in the Goja tracer had been handling errors by panicking and that memory.slice behavior was changed to throw.

2. In eth/tracers/js/goja.go, stackObj.Peek changed to use an error-returning helper and now interrupts the VM and returns nil on error.

3. The same stackObj.Peek path also replaces panic(err) after toBig(...) failure with VM interruption and early return.

4. In the Goja builtin slice helper, fromBuf(...) failures no longer panic; they interrupt the VM and return nil.

5. That slice helper also changes out-of-bounds handling from a log warning to VM interruption with early return.

6. In dbObj.GetState, invalid decoded address or hash inputs no longer panic; they interrupt the VM and return nil.

7. The removed duktape recursion test is engine-cleanup context, not evidence of the root bug in the Goja paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/tracers/js/goja.go | 446 | Goja builtin `slice` helper for tracer-visible memory access; now interrupts on decode and bounds errors |
| eth/tracers/js/goja.go | 598 | stack accessor exposed to JS tracers; now validates peek errors and interrupts instead of panicking |
| eth/tracers/js/goja.go | 687 | state lookup helper exposed to JS tracers; now interrupts on invalid buffer decoding instead of panicking |

## Code Snippets

## Snippet 1

Context: `eth/tracers/js/tracer_test.go:275` (changes bounds, limits, or capacity handling)

Before
```go
}
}

// Tests too deep object / serialization crash for duktape
func TestRecursionLimit(t *testing.T) {
	code := "{step: function() {}, fault: function() {}, result: function() { var o={}; var x=o; for (var i=0; i<1000; i++){  o.foo={}; o=o.foo; } return x; }}"
	fail := "RangeError: json encode recursion limit    in server-side tracer function 'result'"
	tracer, err := newJsTracer(code, nil)
```
After
```go
}
}
```

## Snippet 2

Context: `eth/tracers/js/goja.go:603` (changes bounds, limits, or capacity handling)

Before
```go
func (s *stackObj) Peek(idx int) goja.Value {
	value := s.w.peek(idx)
	res, err := s.toBig(s.vm, value.String())
	if err != nil {
		panic(err)
	}
	return res
```
After
```go
func (s *stackObj) Peek(idx int) goja.Value {
	value, err := s.peek(idx)
	if err != nil {
		s.vm.Interrupt(err)
		return nil
	}
	res, err := s.toBig(s.vm, value.String())
```

## Snippet 3

Context: `eth/tracers/js/goja.go:452` (changes bounds, limits, or capacity handling)

Before
```go
b, err := t.fromBuf(vm, slice, false)
		if err != nil {
			panic(err)
		}
		if start < 0 || start > end || end > len(b) {
			log.Warn("Tracer accessed out of bound memory", "available", len(b), "offset", start, "size", end-start)
		}
		res, err := t.toBuf(vm, b[start:end])
```
After
```go
b, err := t.fromBuf(vm, slice, false)
		if err != nil {
			vm.Interrupt(err)
			return nil
		}
		if start < 0 || start > end || end > len(b) {
			vm.Interrupt(fmt.Sprintf("Tracer accessed out of bound memory: available %d, offset %d, size %d", len(b), start, end-start))
			return nil
```

## Snippet 4

Context: `eth/tracers/js/goja.go:688` (changes a sensitive control or state-update path)

Before
```go
a, err := do.fromBuf(do.vm, addrSlice, false)
	if err != nil {
		panic(err)
	}
	addr := common.BytesToAddress(a)
	h, err := do.fromBuf(do.vm, hashSlice, false)
	if err != nil {
		panic(err)
```
After
```go
a, err := do.fromBuf(do.vm, addrSlice, false)
	if err != nil {
		do.vm.Interrupt(err)
		return nil
	}
	addr := common.BytesToAddress(a)
	h, err := do.fromBuf(do.vm, hashSlice, false)
	if err != nil {
```

# Fix Pattern

Replace panic-on-error and warn-and-continue behavior in tracer host helpers with explicit error checks, VM interruption, and early returns.

## How It Was Fixed

The fix updates Goja tracer helper functions in eth/tracers/js/goja.go so invalid buffer decoding, invalid stack access, conversion errors, and out-of-bounds memory slicing all terminate through vm.Interrupt(...) or do.vm.Interrupt(...) followed by return nil, rather than panicking or continuing after a warning.

# Why It Matters

1. Makes tracer failures explicit and contained within the VM boundary.

2. Avoids panic-based behavior in helper code reachable from tracer execution.

3. Prevents out-of-bounds slice requests from continuing after only a log warning.

4. Still does not by itself prove a remotely exploitable security issue.

# Evidence Notes

Direct evidence supports only a tracing-runtime robustness fix: panic(err) was replaced with vm.Interrupt(err) in multiple helper paths, and out-of-bounds memory.slice changed from warning-only to hard interruption. The supplied material does not prove remote reachability, whole-process crash impact, or a consensus/authentication flaw. The Stop race mentioned in the commit message is not evidenced in the provided hunks. Protocol security invariant: Native Go helpers exposed to the Goja tracer should fail through controlled VM interruption or JS-visible exceptions rather than raw Go panics or permissive continuation after invalid operations. Verification notes: The patch does not show a consensus, authorization, or integrity bug. It is not proven here that a panic escaped all higher-level recovery and crashed the whole node. It is not proven that remote unauthenticated users can reach these tracer code paths in deployment. The commit also contains engine-removal and behavior-cleanup changes, so not every diff hunk is security-relevant. The mentioned `Stop` race is in the commit message but is not evidenced in the provided hunks. The subsystem is eth/tracers/js, not transaction processing. The strongest supported class is panic-on-error with improved bounds/error handling. Security relevance is plausible but unproven from the provided evidence. Helper/test cleanup related to duktape removal should not be treated as the vulnerability root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `panic-on-invalid-input`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `rpc, tracing, js-engine, panic-handling, input-validation`

The patch shows tracer-exposed Go helper functions being changed from raw `panic(err)` or warn-and-continue behavior to controlled `vm.Interrupt(...)` plus early return. That is a real tightening of failure handling at a language/runtime boundary and is plausibly security relevant as hardening against malformed tracer inputs, but the supplied evidence does not prove a concrete exploitable vulnerability, remote reachability, or whole-node crash impact. This fits security hardening better than a confirmed security fix.

## Security Evidence

1. Multiple tracer helper paths replace `panic(err)` with `vm.Interrupt(err)` or `do.vm.Interrupt(err)` and return `nil`.
2. The `slice` helper changes out-of-bounds access from logging a warning and continuing to interrupting execution immediately.
3. Changed functions are exposed to the JS tracer runtime (`Peek`, `slice`, `GetState`), so the patch hardens a host/guest boundary.
4. Commit message explicitly says native Go functions were incorrectly handling errors by panicking and that methods now throw exceptions instead.

## Missing Evidence

1. No evidence that these panic paths could crash the entire node or escape higher-level recovery.
2. No evidence of remote or unauthenticated reachability in deployment from the patch alone.
3. No demonstrated exploit, CVE, incident, or test proving security impact.
4. The mentioned `Stop` race is not supported by the provided hunks.

## Claim Boundaries

1. Supported claim: the patch hardens tracer runtime error handling by replacing panic-based behavior with controlled VM interruption.
2. Supported claim: invalid memory slicing and decode failures now fail closed instead of warning or panicking.
3. Not supported: a confirmed denial-of-service against the full node.
4. Not supported: consensus, authorization, confidentiality, or integrity impact.
5. Not supported: that all touched changes in the engine migration are security relevant.
