---
case_id: case_20240822_f1aa5ae7
project: thor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2024-08-22
source_refs:
  - git:f1aa5ae733617d0366500b3210895415c7068f20
  - "api/debug/debug.go:214"
  - "tracers/tracers.go:96"
  - "cmd/thor/flags.go:167"
  - "tracers/logger/logger.go:124"
bug_class: debug-api-tracer-allowlist-hardening
impact_type:
  - attack-surface-reduction
  - debug-api-abuse-risk
confidence: medium
tags:
  - debug-api
  - tracer-allowlist
  - deny-by-default
  - custom-tracer-gating
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an `api-allowed-tracers` CLI flag defaulting to `none` and changes debug tracer creation to reject blank names and deny tracers unless explicitly allowed or `all` is configured. This is plausibly security-relevant hardening of the debug tracing API, but the evidence does not prove an exploitable vulnerability, external exposure, privilege bypass, or consensus/state impact.

## Observed Patch Facts

1. In `api/debug/debug.go`, the patch replaces `if name == "" {` with `if strings.TrimSpace(name) == "" {`.

2. In `tracers/tracers.go`, the patch replaces `return nil, errors.Wrap(err, "create custom tracer")` with `return nil, errors.Wrap(err, "unable to create custom tracer")`.

3. In `cmd/thor/flags.go`, the patch replaces `// solo mode only flags` with `allowedTracersFlag = cli.StringFlag{`.

4. In `tracers/logger/logger.go`, the patch replaces `func NewStructLogger(cfg json.RawMessage) (*StructLogger, error) {` with `func NewStructLogger(cfg json.RawMessage) (tracers.Tracer, error) {`.

## Project Context

The changed code sits primarily in `api/debug`, `cmd/thor`, `tracers/logger`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `tracers/tracers_test.go`, `tracers/logger/logger_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `tracers/logger/logger_test.go`, `cmd/thor/main.go`. The strongest project-level identifiers around this patch are `name`, `tracer`, `tracers`, and `NewStructLogger`.

## Before/After Behavior

Before the patch, an empty tracer name created the default struct logger, and non-empty names were delegated to the tracer directory, which can create registered tracers and, when custom tracing is allowed, attempt custom JavaScript tracer creation. After the patch, blank or whitespace-only names are rejected, `none` disables tracer creation, and names must be explicitly allowed unless `all` is configured. Tracer creation failures are returned as Forbidden by the trace-call path.

# Root Cause

The previous debug trace API path did not enforce an API-side allowed-tracer policy before constructing tracers. The evidence supports missing configuration-based gating at the API boundary, but not a proven vulnerability root cause beyond that.

## Walkthrough

1. A trace-call request is parsed and passed to `d.createTracer(opt.Name, opt.Config)`.

2. Previously, `name == ""` selected `logger.NewStructLogger(config)`.

3. Previously, non-empty names were passed to `tracers.DefaultDirectory.New(name, config, d.allowCustomTracer)`.

4. The tracer directory can instantiate registered tracers and can evaluate custom JavaScript when existing `allowCustom` behavior permits it.

5. The patch rejects blank or whitespace-only tracer names.

6. The patch checks `d.allowedTracers` for `none`, `all`, and explicit tracer names before creating a tracer.

7. The CLI adds `api-allowed-tracers` with default value `none`, making API tracer creation disabled unless configured.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| api/debug/debug.go | 180 | debug trace-call endpoint parses request options, creates the requested tracer, and returns Forbidden when tracer creation is denied |
| api/debug/debug.go | 214 | central tracer creation guard now rejects blank names and enforces allowedTracers including none/all semantics |
| cmd/thor/flags.go | 167 | node configuration flag api-allowed-tracers defaults tracer access to none |
| tracers/tracers.go | 85 | tracer directory creates built-in tracers or custom JavaScript tracers when custom tracing is allowed |

## Code Snippets

## Snippet 1

Context: `api/debug/debug.go:214` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func (d *Debug) createTracer(name string, config json.RawMessage) (tracers.Tracer, error) {
	if name == "" {
		return logger.NewStructLogger(config)
	}
	return tracers.DefaultDirectory.New(name, config, d.allowCustomTracer)
}
```
After
```go
func (d *Debug) createTracer(name string, config json.RawMessage) (tracers.Tracer, error) {
	if strings.TrimSpace(name) == "" {
		return nil, fmt.Errorf("tracer name must be defined")
	}
	_, noTracers := d.allowedTracers["none"]
	_, allTracers := d.allowedTracers["all"]
```

## Snippet 2

Context: `tracers/tracers.go:96` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
tracer, err := d.jsEval(name, cfg)
		if err != nil {
			return nil, errors.Wrap(err, "create custom tracer")
		}
		return tracer, nil
```
After
```go
tracer, err := d.jsEval(name, cfg)
		if err != nil {
			return nil, errors.Wrap(err, "unable to create custom tracer")
		}
		return tracer, nil
```

## Snippet 3

Context: `cmd/thor/flags.go:167` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// solo mode only flags
	onDemandFlag = cli.BoolFlag{
```
After
```go
}

	allowedTracersFlag = cli.StringFlag{
		Name:  "api-allowed-tracers",
		Value: "none",
		Usage: "define allowed API tracers",
	}
```

## Snippet 4

Context: `tracers/logger/logger.go:124` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// NewStructLogger returns a new logger
func NewStructLogger(cfg json.RawMessage) (*StructLogger, error) {
	var config Config
	if cfg != nil {
```
After
```go
// NewStructLogger returns a new logger
func NewStructLogger(cfg json.RawMessage) (tracers.Tracer, error) {
	var config Config
	if cfg != nil {
```

# Fix Pattern

Add a configuration-driven allowlist check at the API boundary before constructing pluggable tracer implementations, with a deny-by-default setting.

## How It Was Fixed

`cmd/thor/flags.go` adds `api-allowed-tracers` with default `none`. `api/debug/debug.go` updates `createTracer` to require a nonblank name and enforce `allowedTracers` before delegating to the tracer directory. Minor related changes generalize the logger constructor return type and adjust a custom tracer error message.

# Why It Matters

1. Limits tracer construction through the debug API path.

2. Makes tracer availability an explicit operator configuration choice.

3. Reduces unintended exposure of debug tracing behavior.

4. Does not prove remote exploitability or arbitrary code execution from the provided evidence.

5. Does not affect consensus, validator logic, transaction validity, serialization, or persistent chain state.

# Evidence Notes

Grounded evidence comes from `api/debug/debug.go` around `handleTraceCall` and `createTracer`, `cmd/thor/flags.go` adding `api-allowed-tracers`, and `tracers/tracers.go` showing built-in and custom tracer creation behavior. The heuristic baseline's transaction-processing and serialization/state-representation claims are unsupported by the diff and should be discarded. The evidence does not show API authentication, network exposure, attacker capabilities, or a concrete exploit path. Protocol security invariant: The debug trace API should instantiate tracer implementations only when permitted by node configuration. The patch adds an explicit allowed-tracers policy before tracer construction, but the provided evidence does not establish that the prior behavior crossed a security boundary in a deployed configuration. Verification notes: The patch does not prove the debug API is exposed to untrusted users by default. The patch does not prove arbitrary code execution, only that custom tracer creation exists behind existing allowCustom behavior. The patch does not change consensus, validator logic, transaction validity, or persistent chain state. The patch does not show a serialization or canonical state representation fix despite the heuristic baseline. The patch does not prove economic loss or chain integrity impact. Confirmed behavior change: tracer names are now validated and checked against an allowlist. Confirmed default policy from the shown flag is `none`. Confirmed custom JavaScript tracer creation exists only behind existing `allowCustom` behavior. Not confirmed: debug API exposure to untrusted users. Not confirmed: arbitrary code execution vulnerability. Not confirmed: consensus, state, transaction-processing, or serialization impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `debug-api-tracer-allowlist-hardening`
Final impact type: `attack-surface-reduction, debug-api-abuse-risk`
Final confidence: `medium`
Final tags: `debug-api, tracer-allowlist, deny-by-default, custom-tracer-gating, security-hardening`

The patch adds a deny-by-default API tracer policy and enforces an allowlist before constructing tracers, including custom JavaScript tracers when that existing path is enabled. The evidence does not prove an exploitable vulnerability or exposed unauthenticated API, but it clearly tightens security-sensitive debug API behavior. The original transaction-processing, serialization, and state-consistency framing is unsupported and should be replaced with a narrower hardening classification.

## Security Evidence

1. Adds api-allowed-tracers flag with default value none.
2. createTracer now rejects blank or whitespace-only tracer names instead of creating the default logger.
3. createTracer now denies tracer construction unless the requested tracer is explicitly allowed or all is configured.
4. Denied tracer creation returns a Forbidden error from the trace-call API path.
5. Tracer directory can create registered tracers and can evaluate custom JavaScript when allowCustom is enabled.

## Missing Evidence

1. No proof the debug API is exposed to untrusted users by default.
2. No proof of authentication or authorization bypass.
3. No concrete exploit path or attacker capability is shown.
4. No evidence of consensus, validator, transaction validity, serialization, or persistent state impact.
5. No proof that custom JavaScript tracer execution was reachable in a vulnerable deployment configuration.

## Claim Boundaries

1. Keep as security-hardening, not a confirmed vulnerability fix.
2. Do not claim arbitrary code execution from the supplied evidence alone.
3. Do not claim chain integrity, state divergence, or transaction-processing impact.
4. The supported claim is API-side tracer construction is now deny-by-default and allowlist-gated.
