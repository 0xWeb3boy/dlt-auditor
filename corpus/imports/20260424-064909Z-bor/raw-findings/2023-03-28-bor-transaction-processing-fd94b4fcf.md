---
case_id: case_20230328_fd94b4fcf
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2023-03-28
source_refs:
  - git:fd94b4fcfa244179c0500b70fb2944cb686b9ca4
  - "eth/tracers/js/tracer_test.go:151"
  - "eth/tracers/js/goja.go:568"
  - "eth/tracers/tracers.go:97"
  - "eth/tracers/native/call.go:181"
bug_class: resource-exhaustion
impact_type:
  - availability
confidence: medium
tags:
  - security-hardening
  - tracing
  - resource-limits
  - panic-prevention
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided patch clearly hardens tracer memory access and LOG capture against oversized reads by centralizing padded-memory copying behind a size-checked helper. The evidence supports a robustness fix for panic/OOM-like behavior in tracing code, but it does not establish default remote reachability or a confirmed security vulnerability.

## Observed Patch Facts

1. In `eth/tracers/js/tracer_test.go`, the patch replaces `fail: "tracer reached limit for padding memory slice: end 1049600, memorySize 32 at s...` with `fail: "reached limit for padding memory slice: 1049568 at step (<eval>:1:83(20)) in s...`.

2. In `eth/tracers/js/goja.go`, the patch replaces `mlen := mo.memory.Len()` with `slice, err := tracers.GetMemoryCopyPadded(mo.memory, begin, end-begin)`.

3. In `eth/tracers/tracers.go`, the patch adds `const (`.

4. In `eth/tracers/native/call.go`, the patch replaces `data := scope.Memory.GetCopy(int64(mStart.Uint64()), int64(mSize.Uint64()))` with `data, err := tracers.GetMemoryCopyPadded(scope.Memory, int64(mStart.Uint64()), int64(...`.

## Project Context

The changed code sits primarily in `eth/tracers/js`, `eth/tracers`, `eth/tracers/native`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `eth/tracers/tracers_test.go`, `eth/tracers/native/prestate.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `eth/tracers/tracers_test.go`, `eth/tracers/native/prestate.go`. The strongest project-level identifiers around this patch are `memory`, `slice`, `byte`, and `int64`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/flat_calltrace_test.go`, `eth/tracers/internal/tracetest/calltrace_test.go`.

## Before/After Behavior

Before the change, JS tracer memory slicing used local allocation/copy logic in `eth/tracers/js/goja.go`, and native `callTracer` LOG handling in `eth/tracers/native/call.go` copied memory directly from stack-derived sizes. After the change, both paths use `tracers.GetMemoryCopyPadded(...)`, which applies a shared padding limit and returns errors for invalid or oversized requests; the JS path propagates the error, and the native LOG path returns early instead of attempting the copy.

# Root Cause

Tracer memory extraction was handled in multiple places without one shared bounded path. That left JS tracer slicing and native LOG capture dependent on ad hoc copy behavior for large or invalid ranges instead of uniform checked error handling.

## Walkthrough

1. `eth/tracers/tracers.go` adds `memoryPadLimit = 1024 * 1024` and a shared `GetMemoryCopyPadded` helper for bounded zero-padded memory reads.

2. `eth/tracers/js/goja.go` changes `memoryObj.slice` to call the shared helper instead of doing its own allocation/copy sequence.

3. `eth/tracers/native/call.go` changes LOG data extraction to use the same helper and returns when the helper reports an error.

4. `eth/tracers/js/tracer_test.go` keeps an oversized `log.memory.slice(...)` case and updates the expected failure string, showing the path now fails as an error instead of proceeding with the old behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| eth/tracers/tracers.go | 97 | shared helper that enforces padded-memory copy bounds and converts oversized requests into errors |
| eth/tracers/js/goja.go | 568 | JS tracer memory.slice path now uses the bounded helper instead of open-coded allocation/copy |
| eth/tracers/native/call.go | 181 | native callTracer LOG capture now treats unrealistic memory sizes as non-fatal and returns instead of risking panic/OOM |
| eth/tracers/js/tracer_test.go | 151 | regression test asserting oversized tracer memory access fails with an error rather than crashing |

## Code Snippets

## Snippet 1

Context: `eth/tracers/js/tracer_test.go:151` (changes bounds, limits, or capacity handling)

Before
```go
code:     "{res: [], step: function(log) { if (log.op.toString() === 'STOP') { this.res.push(log.memory.slice(5, 1025 * 1024)) } }, fault: function() {}, result: function() { return this.res }}",
			want:     "",
			fail:     "tracer reached limit for padding memory slice: end 1049600, memorySize 32 at step (<eval>:1:83(20))    in server-side tracer function 'step'",
			contract: []byte{byte(vm.PUSH1), byte(0xff), byte(vm.PUSH1), byte(0x00), byte(vm.MSTORE8), byte(vm.STOP)},
		},
	} {
		if have, err := execTracer(tt.code, tt.contract); tt.want != string(have) || tt.fail != err {
			t.Errorf("testcase %d: expected return value to be '%s' got '%s', error to be '%s' got '%s'\n\tcode: %v", i, tt.want, string(have), tt.fail, err, tt.code)
```
After
```go
code:     "{res: [], step: function(log) { if (log.op.toString() === 'STOP') { this.res.push(log.memory.slice(5, 1025 * 1024)) } }, fault: function() {}, result: function() { return this.res }}",
			want:     "",
			fail:     "reached limit for padding memory slice: 1049568 at step (<eval>:1:83(20))    in server-side tracer function 'step'",
			contract: []byte{byte(vm.PUSH1), byte(0xff), byte(vm.PUSH1), byte(0x00), byte(vm.MSTORE8), byte(vm.STOP)},
		},
	} {
		if have, err := execTracer(tt.code, tt.contract); tt.want != string(have) || tt.fail != err {
			t.Errorf("testcase %d: expected return value to be \n'%s'\n\tgot\n'%s'\nerror to be\n'%s'\n\tgot\n'%s'\n\tcode: %v", i, tt.want, string(have), tt.fail, err, tt.code)
```

## Snippet 2

Context: `eth/tracers/js/goja.go:568` (changes bounds, limits, or capacity handling)

Before
```go
return nil, fmt.Errorf("tracer accessed out of bound memory: offset %d, end %d", begin, end)
	}
	mlen := mo.memory.Len()
	if end-int64(mlen) > memoryPadLimit {
		return nil, fmt.Errorf("tracer reached limit for padding memory slice: end %d, memorySize %d", end, mlen)
	}
	slice := make([]byte, end-begin)
	end = min(end, int64(mo.memory.Len()))
```
After
```go
return nil, fmt.Errorf("tracer accessed out of bound memory: offset %d, end %d", begin, end)
	}
	slice, err := tracers.GetMemoryCopyPadded(mo.memory, begin, end-begin)
	if err != nil {
		return nil, err
	}
	return slice, nil
}
```

## Snippet 3

Context: `eth/tracers/tracers.go:97` (changes bounds, limits, or capacity handling)

Before
```go
return true
}
```
After
```go
return true
}

const (
	memoryPadLimit = 1024 * 1024
)

// GetMemoryCopyPadded returns offset + size as a new slice.
```

## Snippet 4

Context: `eth/tracers/native/call.go:181` (changes a sensitive control or state-update path)

Before
```go
}

		data := scope.Memory.GetCopy(int64(mStart.Uint64()), int64(mSize.Uint64()))
		log := callLog{Address: scope.Contract.Address(), Topics: topics, Data: hexutil.Bytes(data)}
		t.callstack[len(t.callstack)-1].Logs = append(t.callstack[len(t.callstack)-1].Logs, log)
```
After
```go
}

		data, err := tracers.GetMemoryCopyPadded(scope.Memory, int64(mStart.Uint64()), int64(mSize.Uint64()))
		if err != nil {
			// mSize was unrealistically large
			return
		}
```

# Fix Pattern

Centralize edge-case memory copying in a shared helper with explicit size limits, and convert oversized tracer operations into ordinary errors or early exits.

## How It Was Fixed

A new shared padded-memory helper was introduced with a 1 MiB padding cap. The JS tracer now delegates memory slicing to that helper, and native call tracing uses the same helper for LOG data and skips capture on oversized requests.

# Why It Matters

1. Removes duplicated tracer memory-copy logic.

2. Bounds oversized padded reads in one place.

3. Turns oversized trace inputs into controlled failures.

4. Improves tracer stability without showing a consensus-rule change.

# Evidence Notes

Direct code evidence shows bounded-memory hardening in `eth/tracers/tracers.go`, `eth/tracers/js/goja.go`, `eth/tracers/native/call.go`, and a regression test in `eth/tracers/js/tracer_test.go`. The commit message also mentions OOM panic and opcode-validation panic handling, including `prestateTracer`, but the provided excerpts do not directly show the `prestateTracer` change or prove exploitability beyond the tracer subsystem. Protocol security invariant: Tracer-visible EVM memory reads should be bounded and fail with explicit errors rather than triggering panics or very large allocations during trace collection. Verification notes: The patch does not show a consensus, authorization, or fund-safety flaw. The excerpt does not prove that untrusted remote users can reach these tracer paths in a default deployment. Commit text mentions prestateTracer panic handling, but the provided diff evidence does not show that exact code path. No evidence here supports claims of code execution, persistent corruption, or state divergence. The supplied diff supports a tracer hardening change. The supplied diff does not prove remote exploit reachability. The supplied excerpts do not directly show the `prestateTracer` fix mentioned in the commit message. No evidence here shows consensus impact, authorization bypass, or fund-safety impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `security-hardening, tracing, resource-limits, panic-prevention`

The patch evidence supports retaining this as a security-hardening case, not a confirmed security fix. The code centralizes bounded padded-memory reads, adds a 1 MiB limit, and converts oversized tracer operations from panic/OOM-prone behavior into ordinary errors or early returns. That is a meaningful hardening change against availability loss in a tracing subsystem, but the supplied diff does not by itself prove default remote reachability, exploitability, or a concrete externally triggerable vulnerability.

## Security Evidence

1. A shared helper adds an explicit `memoryPadLimit = 1024 * 1024` for padded memory copies.
2. `memoryObj.slice` stops doing ad hoc allocation/copy and now returns helper errors for oversized requests.
3. `callTracer` LOG capture switches from direct memory copy to the bounded helper and aborts on unrealistic sizes.
4. Regression test covers an oversized `log.memory.slice(...)` case and expects a controlled error instead of unsafe behavior.
5. Commit message explicitly mentions fixing OOM panic and panic-on-validation-error behavior in tracers.

## Missing Evidence

1. No patch excerpt proves these tracer paths are reachable by untrusted remote users in a default deployment.
2. The provided hunks do not show the `prestateTracer` or opcode-validation panic fixes mentioned in the commit message.
3. No evidence quantifies whether the prior behavior caused process crash, node crash, or only tracer failure in request scope.
4. No advisory, CVE, or exploit narrative is provided.

## Claim Boundaries

1. Supported claim: the commit hardens tracer memory handling and panic resistance against oversized or invalid trace inputs.
2. Not supported from this patch alone: a confirmed remotely exploitable denial-of-service vulnerability.
3. Not supported from the excerpts: consensus impact, authorization bypass, fund risk, or code execution.
4. Classification should stay at security hardening rather than a concrete security-fix claim.
