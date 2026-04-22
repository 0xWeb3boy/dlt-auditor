---
case_id: case_20200129_f8809788d
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
bug_class: input-validation
impact_type:
  - correctness-or-hardening
source_quality: medium
date: 2020-01-29
source_refs:
  - git:f8809788d2f5449c7049ff3202448eaf060b080d
  - "go/registry/api/sanity_check.go:88"
  - "go/registry/api/api.go:1014"
  - "go/registry/api/api.go:1082"
  - "go/registry/api/api.go:513"
confidence: medium
tags:
  - registry
  - genesis
  - input-validation
  - access-control
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports that this commit tightens registry and genesis sanity checks, but it does not establish a concrete vulnerability or exploitable security flaw. The strongest grounded claim is additional admission-time validation for node/runtime descriptors and cross-runtime references.

## Observed Patch Facts

1. In `go/registry/api/sanity_check.go`, the patch replaces `return newSanityCheckRuntimeLookup(seenRuntimes, seenSuspendedRuntimes), nil` with `// Then build a runtime lookup table and re-check compute runtimes as those need to r...`.

2. In `go/registry/api/api.go`, the patch replaces `// Ensure there is at least one member of the transaction scheduler group.` with `// Ensure there is at least one member of the compute group.`.

3. In `go/registry/api/api.go`, the patch replaces `// Ensure there is at least one member of the compute group.` with `// Ensure a valid TEE hardware is specified.`.

4. In `go/registry/api/api.go`, the patch replaces `runtimes = append(runtimes, regRt)` with `// Enforce what kinds of runtimes are allowed.`.

## Project Context

The changed code sits primarily in `go/registry/api`, `go/registry`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/registry/api/runtime.go`, `go/registry/api/grpc.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/registry/api/runtime.go`, `go/registry/api/grpc.go`. The strongest project-level identifiers around this patch are `group`, `runtime`, `runtimes`, and `Errorf`. Nearby tests or test-like files include `go/registry/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown code accepted some node/runtime descriptors without checking node-role-to-runtime-kind compatibility at that point, did not reject zero-sized executor or merge groups in the shown compute-runtime path, and returned the runtime lookup immediately after initial per-runtime verification. After the patch, node registration rejects disallowed runtime kinds for the node's roles, compute runtime registration rejects zero-sized executor and merge groups, and runtime sanity checking builds the lookup with error handling and re-checks compute runtimes against referenced key manager runtimes.

# Root Cause

Incomplete registry admission sanity checks: some descriptor constraints were either not enforced in the shown path or were only checked after insufficient context had been assembled.

## Walkthrough

1. `VerifyRegisterNodeArgs` now rejects `KindKeyManager` and `KindCompute` runtime advertisements when the node lacks the corresponding allowed roles.

2. `VerifyRegisterRuntimeArgs` now rejects compute runtimes with `Executor.GroupSize == 0` and `Merge.GroupSize == 0`.

3. `SanityCheckRuntimes` no longer returns the lookup immediately; it now builds the lookup, handles lookup-construction errors, and performs an additional pass for compute runtimes so key-manager references can be validated against the assembled runtime set.

4. The supplied evidence shows stricter descriptor validation, but not a demonstrated attack path, privilege escalation, or consensus break.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/registry/api/api.go | 513 | Node registration validation now enforces that advertised compute and key-manager runtimes match the node's allowed roles. |
| go/registry/api/api.go | 983 | Runtime registration validation rejects invalid runtime descriptors with zero-sized executor or merge groups before admission. |
| go/registry/api/sanity_check.go | 65 | Registry/genesis sanity checking now rebuilds runtime lookup and revalidates compute runtimes against referenced key-manager runtimes. |

## Code Snippets

## Snippet 1

Context: `go/registry/api/sanity_check.go:88` (changes a sensitive control or state-update path)

Before
```go
}

	return newSanityCheckRuntimeLookup(seenRuntimes, seenSuspendedRuntimes), nil
}
```
After
```go
}

	// Then build a runtime lookup table and re-check compute runtimes as those need to reference
	// correct key manager runtimes when a key manager is configured.
	lookup, err := newSanityCheckRuntimeLookup(seenRuntimes, seenSuspendedRuntimes)
	if err != nil {
		return nil, fmt.Errorf("runtime sanity check failed: %w", err)
	}
```

## Snippet 2

Context: `go/registry/api/api.go:1014` (changes a sensitive control or state-update path)

Before
```go
}

		// Ensure there is at least one member of the transaction scheduler group.
		if rt.TxnScheduler.GroupSize == 0 {
```
After
```go
}

		// Ensure there is at least one member of the compute group.
		if rt.Executor.GroupSize == 0 {
			logger.Error("RegisterRuntime: executor group size too small",
				"runtime", rt,
			)
			return nil, fmt.Errorf("%w: executor group too small", ErrInvalidArgument)
```

## Snippet 3

Context: `go/registry/api/api.go:1082` (changes a sensitive control or state-update path)

Before
```go
}

	// Ensure there is at least one member of the compute group.
	if rt.Executor.GroupSize == 0 {
		logger.Error("RegisterRuntime: executor group size too small",
			"runtime", rt,
		)
		return nil, fmt.Errorf("%w: executor group too small", ErrInvalidArgument)
```
After
```go
}

	// Ensure a valid TEE hardware is specified.
	if rt.TEEHardware >= node.TEEHardwareReserved {
```

## Snippet 4

Context: `go/registry/api/api.go:513` (changes a sensitive control or state-update path)

Before
```go
}

			runtimes = append(runtimes, regRt)
		}
```
After
```go
}

			// Enforce what kinds of runtimes are allowed.
			if regRt.Kind == KindKeyManager && !n.HasRoles(KeyManagerRuntimeAllowedRoles) {
				return nil, nil, fmt.Errorf("%w: key manager runtime not allowed", ErrInvalidArgument)
			}
			if regRt.Kind == KindCompute && !n.HasRoles(ComputeRuntimeAllowedRoles) {
				return nil, nil, fmt.Errorf("%w: compute runtime not allowed", ErrInvalidArgument)
```

# Fix Pattern

Add stricter admission-time sanity checks, including role/type checks, required non-zero fields, and lookup-backed cross-reference validation.

## How It Was Fixed

The patch adds explicit node-role checks for advertised runtime kinds, explicit non-zero group-size checks for compute runtimes, and a second validation phase that uses a built runtime lookup to re-check compute runtime references.

# Why It Matters

1. Prevents inconsistent registry descriptors from being admitted through the shown paths.

2. Catches malformed compute runtime configurations earlier.

3. Validates cross-runtime references with full lookup context instead of only per-object checks.

4. Improves registry/genesis correctness even though security impact is not proven by the evidence.

# Evidence Notes

The evidence is concentrated in `go/registry/api/api.go` and `go/registry/api/sanity_check.go`. It clearly shows added validation and sanity checks. It does not show that signature verification changed, that an attacker could reach these paths without existing authority, or that the prior behavior led to exploitable privilege gain or confidentiality/integrity compromise. The commit subject also mentions test fixes and sanity checks, which supports a cautious classification. Protocol security invariant: Registry admission should reject descriptors that are internally malformed or inconsistent with role and runtime-reference constraints before they enter registry or genesis state. Verification notes: The patch does not prove an unauthenticated attacker could submit these registry objects. It does not show signature verification was broken; signature handling is unchanged in the provided evidence. It does not establish consensus takeover, key compromise, or data confidentiality impact. Some touched files are test and genesis support updates, which may be regression coverage rather than part of the security fix itself. No provided evidence demonstrates a concrete exploit scenario. No provided evidence shows broken authentication or signature verification. The role checks are security-relevant in flavor, but the impact of their prior absence is not established here. The patch is best treated as registry hardening/correctness work with unclear security status. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final confidence: `medium`
Final tags: `registry, genesis, input-validation, access-control, security-hardening`

The patch clearly adds stricter validation in security-sensitive registry/genesis admission paths: nodes can no longer advertise runtime kinds outside their allowed roles, compute runtimes must have non-zero executor and merge groups, and compute runtimes are rechecked against key-manager references after lookup construction. That is strong evidence of security hardening around policy enforcement and state admission, but the supplied diff does not prove a concrete exploitable vulnerability, authentication bypass, or prior compromise path. The most defensible corpus label is security-hardening rather than security-fix.

## Security Evidence

1. Node registration now rejects key-manager and compute runtimes when the node lacks the corresponding allowed roles.
2. Runtime registration now rejects zero-sized executor and merge groups for compute runtimes.
3. Runtime sanity checking now builds a lookup and re-validates compute runtimes against referenced key-manager runtimes.
4. The changes affect registry/genesis validation logic, not only tests or refactoring.

## Missing Evidence

1. No proof that the pre-patch behavior enabled attacker-controlled privilege gain or registry abuse.
2. No evidence that signature verification, authentication, or enclave attestation was previously bypassable.
3. No advisory, regression test, or commit message text describing a concrete security exploit or incident.

## Claim Boundaries

1. Supported: the commit tightens admission-time validation and policy enforcement for registry/genesis objects.
2. Supported: the role-to-runtime-kind checks are security-relevant hardening in a sensitive consensus-adjacent subsystem.
3. Not supported: the patch fixes a demonstrated exploitable vulnerability or consensus takeover bug.
4. Not supported: the patch directly changes cryptographic verification or signature handling.
