---
case_id: case_20210913_b8d7c662c
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2021-09-13
source_refs:
  - git:b8d7c662cd8f87f7dae15c7a53be25ec527999cd
  - "cmd/evm/disasm.go:47"
  - "core/vm/logger.go:47"
  - "cmd/evm/main.go:126"
  - "core/vm/logger_json.go:68"
bug_class: trace-output-exposure-hardening
impact_type:
  - trace-data-exposure
confidence: medium
tags:
  - security-hardening
  - evm-tracing
  - logging-defaults
  - opt-in-capture
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes EVM trace logging defaults so memory and return data are no longer emitted by default. That is supported as a tracing hardening or correctness change, but the supplied evidence does not establish a concrete vulnerability or exploit scenario.

## Observed Patch Facts

1. In `cmd/evm/disasm.go`, the patch replaces `return errors.New("Missing filename or --input value")` with `return errors.New("missing filename or --input value")`.

2. In `core/vm/logger.go`, the patch replaces `DisableMemory bool // disable memory capture` with `EnableMemory bool // enable memory capture`.

3. In `cmd/evm/main.go`, the patch replaces `DisableReturnDataFlag = cli.BoolFlag{` with `DisableReturnDataFlag = cli.BoolTFlag{`.

4. In `core/vm/logger_json.go`, the patch replaces `if !l.cfg.DisableReturnData {` with `if l.cfg.EnableReturnData {`.

## Project Context

The changed code sits primarily in `cmd/evm`, `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/vm/stack.go`, `core/vm/interpreter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/interpreter.go`, `core/vm/access_list_tracer.go`. The strongest project-level identifiers around this patch are `capture`, `disable`, `output`, and `data`.

## Before/After Behavior

Before the patch, trace configuration used negative flags like `DisableMemory` and `DisableReturnData`, and the shown logger code emitted return data unless disabled. After the patch, configuration uses `EnableMemory` and `EnableReturnData`, and the shown logger code emits those fields only when explicitly enabled; the CLI flag wiring is adjusted to preserve names while changing defaults.

# Root Cause

The trace configuration used permissive default semantics for verbose fields by expressing them as disable-flags, so zero-value/default behavior included memory and return data unless callers turned them off.

## Walkthrough

1. `core/vm/logger.go` changes trace config fields from `DisableMemory`/`DisableReturnData` to `EnableMemory`/`EnableReturnData`.

2. `core/vm/logger_json.go` changes return-data emission from `if !l.cfg.DisableReturnData` to `if l.cfg.EnableReturnData`, and the provided context shows memory behind `if l.cfg.EnableMemory`.

3. `cmd/evm/main.go` changes the `noreturndata` CLI flag type and usage text, which supports a default-behavior change while keeping the flag name.

4. The surrounding interpreter context only shows that the logger consumes transient execution state; it does not prove a consensus, authorization, or remotely exploitable issue.

5. The `cmd/evm/disasm.go` string capitalization change is incidental and should not be treated as security evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/logger.go | 47 | trace configuration surface; changes capture defaults from disable-flags to opt-in enable-flags |
| core/vm/logger_json.go | 68 | structured trace serializer; stops including return data unless explicitly enabled |
| cmd/evm/main.go | 126 | CLI flag wiring; preserves flags while changing default behavior for trace verbosity |

## Code Snippets

## Snippet 1

Context: `cmd/evm/disasm.go:47` (changes a sensitive control or state-update path)

Before
```go
in = ctx.GlobalString(InputFlag.Name)
	default:
		return errors.New("Missing filename or --input value")
	}
```
After
```go
in = ctx.GlobalString(InputFlag.Name)
	default:
		return errors.New("missing filename or --input value")
	}
```

## Snippet 2

Context: `core/vm/logger.go:47` (changes bounds, limits, or capacity handling)

Before
```go
// LogConfig are the configuration options for structured logger the EVM
type LogConfig struct {
	DisableMemory     bool // disable memory capture
	DisableStack      bool // disable stack capture
	DisableStorage    bool // disable storage capture
	DisableReturnData bool // disable return data capture
	Debug             bool // print output during capture end
	Limit             int  // maximum length of output, but zero means unlimited
```
After
```go
// LogConfig are the configuration options for structured logger the EVM
type LogConfig struct {
	EnableMemory     bool // enable memory capture
	DisableStack     bool // disable stack capture
	DisableStorage   bool // disable storage capture
	EnableReturnData bool // enable return data capture
	Debug            bool // print output during capture end
	Limit            int  // maximum length of output, but zero means unlimited
```

## Snippet 3

Context: `cmd/evm/main.go:126` (changes a sensitive control or state-update path)

Before
```go
Usage: "disable storage output",
	}
	DisableReturnDataFlag = cli.BoolFlag{
		Name:  "noreturndata",
		Usage: "disable return data output",
	}
)
```
After
```go
Usage: "disable storage output",
	}
	DisableReturnDataFlag = cli.BoolTFlag{
		Name:  "noreturndata",
		Usage: "enable return data output",
	}
)
```

## Snippet 4

Context: `core/vm/logger_json.go:68` (changes a sensitive control or state-update path)

Before
```go
log.Stack = stack.data
	}
	if !l.cfg.DisableReturnData {
		log.ReturnData = rData
	}
```
After
```go
log.Stack = stack.data
	}
	if l.cfg.EnableReturnData {
		log.ReturnData = rData
	}
```

# Fix Pattern

Invert verbose trace fields from default-on disable-flags to explicit enable-flags, and align CLI defaults with the new opt-in behavior.

## How It Was Fixed

The fix redefined the relevant logger configuration fields as positive enable-flags and updated the JSON logger to serialize memory and return data only when those flags are set. The CLI wiring was then adjusted so the user-facing flags remain available while the default trace output becomes less verbose.

# Why It Matters

1. Default traces become less verbose and more bounded.

2. Large transient fields are no longer included unless explicitly requested.

3. The evidence supports tracing hardening, not a proven vulnerability fix.

# Evidence Notes

Strong evidence exists for a default-behavior change in trace logging: `core/vm/logger.go`, `core/vm/logger_json.go`, and `cmd/evm/main.go` all align on opt-in memory/return-data capture. The provided material does not show an actual exploit, affected RPC surface, confidentiality breach, or denial-of-service condition. Test files are listed in commit metadata, but no test hunks were provided here, so regression intent cannot be verified from the supplied evidence alone. Protocol security invariant: Structured EVM traces should only include large transient execution artifacts such as memory dumps and return data when explicitly enabled; the provided evidence does not establish a broader security invariant beyond trace-output defaults. Verification notes: The patch does not prove a remotely exploitable denial-of-service condition. The patch does not show any consensus, state-transition, or authorization bug. It is not proven that sensitive data became exposed outside explicitly requested tracing output. The visible diff supports hardening of defaults more clearly than remediation of a demonstrated exploit path. No provided hunk demonstrates attacker control or cross-trust-boundary impact. No evidence here proves remote exploitability, consensus impact, or unauthorized disclosure. The safest classification from the supplied input is security relevance unclear, with exclusion from a security-fix corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `trace-output-exposure-hardening`
Final impact type: `trace-data-exposure`
Final confidence: `medium`
Final tags: `security-hardening, evm-tracing, logging-defaults, opt-in-capture`

The supplied patch consistently changes EVM trace logging from default-on capture of memory and return data to explicit opt-in capture. That is a meaningful tightening of a security-sensitive output path, because it reduces default exposure of detailed execution artifacts. However, the evidence does not prove a concrete exploit, attacker-triggered path, or confirmed confidentiality incident, so this is better classified as security hardening rather than a demonstrated security fix.

## Security Evidence

1. `core/vm/logger.go` replaces `DisableMemory` and `DisableReturnData` with `EnableMemory` and `EnableReturnData`, changing the default semantics to opt-in capture.
2. `core/vm/logger_json.go` now emits `Memory` and `ReturnData` only when the corresponding enable flags are set.
3. `cmd/evm/main.go` preserves the user-facing flag while changing the default behavior so return-data output is no longer emitted unless enabled.
4. The commit subject explicitly states that memory output is disabled by default in traces, matching the code changes.

## Missing Evidence

1. No provided hunk shows the RPC-facing call path or another cross-trust-boundary surface consuming these traces.
2. No supplied test diff or bug report demonstrates an actual information leak, exploit, or user-impacting incident.
3. No evidence shows attacker control, privilege bypass, or a remotely triggerable denial-of-service condition.

## Claim Boundaries

1. The patch supports a claim of hardening trace-output defaults, not a proven vulnerability remediation.
2. The evidence does not support claims about consensus safety, authorization flaws, or state-transition bugs.
3. The `disasm.go` capitalization change is incidental and should not be treated as security evidence.
