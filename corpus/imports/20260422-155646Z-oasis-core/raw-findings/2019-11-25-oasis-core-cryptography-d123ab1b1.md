---
case_id: case_20191125_d123ab1b1
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: medium
date: 2019-11-25
source_refs:
  - git:d123ab1b1e6fb2a4cc76f55be4f36ed11df30e1b
  - "go/worker/registration/worker.go:388"
  - "go/worker/common/p2p/p2p.go:116"
  - "go/worker/registration/worker.go:558"
  - "go/worker/registration/worker.go:289"
bug_class: insufficient-identity-validation
impact_type:
  - integrity
confidence: medium
tags:
  - registry
  - node-registration
  - identity-validation
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a registration-path hardening change: validator consensus addresses are now filtered for valid IDs, roles are attached explicitly before role-specific hooks run, and optional addresses are only added when the node has roles that require them. The provided hunks do not establish a concrete exploitable vulnerability or show that invalid registrations were previously accepted in a way that caused a security break.

## Observed Patch Facts

1. In `go/worker/registration/worker.go`, the patch replaces `if len(addrs) == 0 {` with `var validatedAddrs []node.ConsensusAddress`.

2. In `go/worker/common/p2p/p2p.go`, the patch replaces `id, err := peerIDToPublicKey(p.host.ID())` with `return addresses`.

3. In `go/worker/registration/worker.go`, the patch replaces `roleHooks: []func(*node.Node) error{},` with `roleHooks: make(map[node.RolesMask](func(*node.Node) error)),`.

4. In `go/worker/registration/worker.go`, the patch replaces `for _, h := range w.roleHooks {` with `for role, h := range w.roleHooks {`.

## Project Context

The changed code sits primarily in `go/worker/registration`, `go/worker`, `go/worker/common/p2p`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/worker/common/p2p/types.go`, `go/worker/common/p2p/stream.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/storage/committee/node.go`, `go/worker/keymanager/worker.go`. The strongest project-level identifiers around this patch are `role`, `addr`, `roleHooks`, and `logger`. Nearby tests or test-like files include `go/worker/txnscheduler/tests/tester.go`, `go/worker/txnscheduler/algorithm/tests/tester.go`.

## Before/After Behavior

Before the change, the registration worker used unkeyed role hooks, added role-dependent data without an explicit per-hook role attachment in the shown code, and the validator path only showed a coarse non-empty address check before later validation. After the change, role hooks are keyed by role, `registerNode` adds each role before running its hook, committee addresses are only included when required by the node's roles, and validator consensus addresses with invalid `addr.ID` values are skipped before address verification.

# Root Cause

The registration code was assembling node descriptors with weaker coupling between advertised roles and role-specific fields, and it did not explicitly reject validator consensus addresses whose embedded identity was invalid before building the registration payload.

## Walkthrough

1. `registerNode` constructs a local `nodeDesc` and then applies worker role hooks during registration.

2. The patch changes `roleHooks` from a slice to a `map[node.RolesMask](func(*node.Node) error)`, and registration startup now registers the validator hook together with `node.RoleValidator`.

3. During registration, the patched code iterates `for role, h := range w.roleHooks`, calls `nodeDesc.AddRoles(role)`, and then runs the hook.

4. The same registration path now only adds committee addresses when `nodeDesc.HasRoles(registry.CommitteeAddressRequiredRoles)` is true.

5. In `consensusValidatorHook`, the patch introduces `validatedAddrs` and skips any consensus address whose `addr.ID` is not valid.

6. Remaining addresses are still passed through `registry.VerifyAddress(...)` before being used.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/worker/registration/worker.go | 261 | builds the node descriptor during registration and now ties advertised roles to role-specific hooks and optional address inclusion |
| go/worker/registration/worker.go | 346 | validates consensus validator addresses and rejects entries with invalid identity bindings before registration |
| go/worker/registration/worker.go | 502 | initializes role-aware registration hooks so role assignment and registration data stay consistent |
| go/worker/common/p2p/p2p.go | 116 | packages P2P identity/address information used in node registration |

## Code Snippets

## Snippet 1

Context: `go/worker/registration/worker.go:388` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	if len(addrs) == 0 {
		w.logger.Error("node has no consensus addresses, not registering as validator")
		return nil
	}

	// TODO: Someone, somewhere needs to check to see if the address is
```
After
```go
}

	var validatedAddrs []node.ConsensusAddress
	for _, addr := range addrs {
		if !addr.ID.IsValid() {
			w.logger.Error("worker/registration: skipping validator address due to invalid ID",
				"addr", addr,
			)
```

## Snippet 2

Context: `go/worker/common/p2p/p2p.go:116` (changes a sensitive control or state-update path)

Before
```go
}

	id, err := peerIDToPublicKey(p.host.ID())
	if err != nil {
		panic(err)
	}

	return node.P2PInfo{
```
After
```go
}

	return addresses
}
```

## Snippet 3

Context: `go/worker/registration/worker.go:558` (changes a consensus- or validator-sensitive branch)

Before
```go
consensus:          consensus,
		p2p:                p2p,
		roleHooks:          []func(*node.Node) error{},
	}

	if flags.ConsensusValidator() {
		w.RegisterRole(w.consensusValidatorHook)
	}
```
After
```go
consensus:          consensus,
		p2p:                p2p,
		roleHooks:          make(map[node.RolesMask](func(*node.Node) error)),
	}

	if flags.ConsensusValidator() {
		if err := w.RegisterRole(node.RoleValidator, w.consensusValidatorHook); err != nil {
			return nil, err
```

## Snippet 4

Context: `go/worker/registration/worker.go:289` (changes an authorization or privilege gate)

Before
```go
// Apply worker role hooks:
	for _, h := range w.roleHooks {
		if err := h(&nodeDesc); err != nil {
			w.logger.Error("failed to apply role hook",
				"err", err)
		}
	}
```
After
```go
// Apply worker role hooks:
	for role, h := range w.roleHooks {
		nodeDesc.AddRoles(role)

		if err := h(&nodeDesc); err != nil {
			w.logger.Error("failed to apply role hook",
				"role", role,
```

# Fix Pattern

Tighten registration-time validation by rejecting malformed identity-bearing fields early, key hook execution to explicit roles, and omit optional descriptor fields unless the advertised role requires them.

## How It Was Fixed

The fix makes role handling explicit in the registration worker, adds roles to the descriptor before applying the corresponding hook, gates committee-address registration on role requirements, and filters validator consensus addresses so entries with invalid IDs are dropped before address verification.

# Why It Matters

1. Reduces malformed node descriptors in registry state.

2. Keeps advertised roles aligned with the role-specific fields that get populated.

3. Limits unnecessary optional address publication.

4. The visible impact is strongest as correctness and liveness hardening, not a demonstrated security exploit.

# Evidence Notes

The direct evidence is limited to registration-worker changes and a partial P2P hunk. It clearly shows added ID validation for validator addresses and stricter role/optional-address handling, but it does not show registry-side acceptance behavior, a demonstrated bypass, or concrete attacker-controlled exploitation. The P2P snippet is incomplete, so stronger claims about identity-source changes there are not well supported. Protocol security invariant: Registry descriptors should only advertise addresses that carry valid identities, and optional address fields should only be included for roles that actually require them. Verification notes: The patch does not prove that an external attacker could force acceptance of a forged node identity. The evidence does not show a confidentiality or integrity break; the clearest impact is malformed registry state or routing/liveness issues. The provided hunks do not establish that signature verification or consensus authorization was previously bypassed. The exact registry-side rejection logic is not shown, so remote exploitability remains unproven. No provided hunk shows a full before/after registry acceptance path. No evidence demonstrates confidentiality, integrity, or authorization impact. The supplied P2P diff is partial and should not carry major security conclusions by itself. A security relevance argument is plausible, but the vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-identity-validation`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `registry, node-registration, identity-validation, validator`

The patch is best treated as security hardening. It tightens registration of security-sensitive node metadata by requiring valid identities on advertised validator addresses, coupling role-specific hooks to explicit roles, and omitting optional addresses unless the node role requires them. That supports a security-oriented integrity hardening interpretation for registry state, but the provided evidence does not prove a concrete exploitable vulnerability, prior authorization bypass, or consensus compromise.

## Security Evidence

1. Validator registration now skips consensus addresses whose embedded ID is invalid.
2. Role hooks are keyed by explicit roles and roles are added to the node descriptor before hook execution.
3. Optional committee addresses are only included when the node's roles require them.
4. Commit metadata says the registry now validates optional node addresses and the worker only registers required info.

## Missing Evidence

1. No registry-side before/after acceptance path is shown proving malformed registrations were previously accepted.
2. No evidence shows an attacker could exploit invalid addresses to impersonate a node or bypass authorization.
3. No concrete confidentiality, integrity, or consensus failure scenario is demonstrated from the patch alone.
4. The P2P hunk is incomplete and does not support stronger claims about identity handling by itself.

## Claim Boundaries

1. This supports descriptor and registration hardening, not a proven exploitable vulnerability.
2. Do not claim signature verification, authentication, or consensus authorization was previously bypassed.
3. Do not classify this as a liveness-only fix; the clearer issue is validation of identity-bearing registration data.
4. The strongest justified corpus label is security-hardening, not security-fix.
