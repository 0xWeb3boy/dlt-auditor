---
case_id: case_20240316_68133d1f3
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2024-03-16
source_refs:
  - git:68133d1f369677e6417f18e4a4a1610f61af63f9
  - "go/consensus/cometbft/apps/keymanager/churp/txs.go:227"
  - "keymanager/src/churp/handler.rs:216"
  - "keymanager/src/churp/handler.rs:127"
  - "go/worker/keymanager/churp.go:251"
bug_class: protocol-state-confusion
impact_type:
  - integrity
confidence: medium
tags:
  - consensus
  - keymanager
  - churp
  - cryptographic-protocol
  - epoch-handoff
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch consistently replaces `round`-based checks and storage keys with `handoff`/`next_handoff` in CHURP consensus, runtime, persistence, and worker code. That is strong evidence of a protocol/state-consistency fix, but the provided evidence does not prove an exploitable vulnerability or a concrete security impact.

## Observed Patch Facts

1. In `go/consensus/cometbft/apps/keymanager/churp/txs.go`, the patch replaces `if status.Round != req.Application.Round {` with `if status.NextHandoff != req.Application.Handoff {`.

2. In `keymanager/src/churp/handler.rs`, the patch replaces `// polynomial is generated per round upon restarts, unless a malicious` with `// polynomial is generated per handoff upon restarts, unless a malicious`.

3. In `keymanager/src/churp/handler.rs`, the patch replaces `if status.round != req.round {` with `if status.next_handoff != req.handoff {`.

4. In `go/worker/keymanager/churp.go`, the patch replaces `// Stop and remove submission for the previous round.` with `// Stop and remove submission for the previous handoff.`.

## Project Context

The changed code sits primarily in `go/consensus/cometbft/apps/keymanager/churp`, `go/consensus/cometbft/apps/keymanager`, `keymanager/src/churp`, which anchors the finding in the `storage` area of the project. Historical context from `go/worker/keymanager/worker.go`, `go/worker/keymanager/status.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/keymanager/worker.go`, `go/worker/keymanager/secrets.go`. The strongest project-level identifiers around this patch are `status`, `round`, `handoff`, and `D::PrimeField`. Nearby tests or test-like files include `go/worker/compute/executor/tests/tester.go`, `go/worker/storage/tests/tester.go`.

## Before/After Behavior

Before the patch, several CHURP paths compared requests or keyed local state using `round`; after the patch, those same paths use `handoff` or `next_handoff`. This includes consensus-side request validation, runtime-side init validation, persisted polynomial lookup across restarts, and worker stale-submission retirement.

# Root Cause

Inconsistent use of two related state coordinates (`round` versus `handoff`) across the CHURP subsystem. The evidence shows that some paths were bound to `round` even though surrounding logic and comments indicate the operation is scoped to a handoff epoch.

## Walkthrough

1. `go/consensus/cometbft/apps/keymanager/churp/txs.go` changes request validation from `status.Round`/`req.Application.Round` to `status.NextHandoff`/`req.Application.Handoff`.

2. `keymanager/src/churp/handler.rs` changes init-time validation from `status.round`/`req.round` to `status.next_handoff`/`req.handoff`.

3. The same Rust handler changes persisted polynomial reload from `load_bivariate_polynomial(..., round)` to `load_bivariate_polynomial(..., handoff)`, with comments updated from 'per round' to 'per handoff'.

4. `go/worker/keymanager/churp.go` changes stale submission retirement from round advancement to handoff advancement.

5. Taken together, the diff shows subsystem-wide alignment on handoff epoch as the identifier for this workflow.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/cometbft/apps/keymanager/churp/txs.go | 198 | consensus application path that accepts signed CHURP applications only for the currently scheduled handoff epoch |
| go/consensus/cometbft/apps/keymanager/churp/txs.go | 227 | request-field validation changed from `status.Round` to `status.NextHandoff` |
| keymanager/src/churp/handler.rs | 121 | runtime/keymanager init path now verifies the request against `status.next_handoff` instead of `status.round` |
| keymanager/src/churp/handler.rs | 192 | dealer creation and local polynomial reload are keyed by handoff epoch across restarts |
| go/worker/keymanager/churp.go | 241 | worker submission scheduler now retires stale submissions based on handoff advancement |

## Code Snippets

## Snippet 1

Context: `go/consensus/cometbft/apps/keymanager/churp/txs.go:227` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	if status.Round != req.Application.Round {
		return fmt.Errorf("keymanager: churp: invalid round: got %d, expected %d", req.Application.Round, status.Round)
	}
```
After
```go
}

	if status.NextHandoff != req.Application.Handoff {
		return fmt.Errorf("keymanager: churp: invalid handoff: got %d, expected %d", req.Application.Handoff, status.NextHandoff)
	}
```

## Snippet 2

Context: `keymanager/src/churp/handler.rs:216` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
// Check the local storage to ensure that only one secret bivariate
        // polynomial is generated per round upon restarts, unless a malicious
        // host has cleared the storage.
        let polynomial = self
            .storage
            .load_bivariate_polynomial::<D::PrimeField>(churp_id, round);
        let polynomial = match polynomial {
```
After
```rust
// Check the local storage to ensure that only one secret bivariate
        // polynomial is generated per handoff upon restarts, unless a malicious
        // host has cleared the storage.
        let polynomial = self
            .storage
            .load_bivariate_polynomial::<D::PrimeField>(churp_id, handoff);
        let polynomial = match polynomial {
```

## Snippet 3

Context: `keymanager/src/churp/handler.rs:127` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
return Err(Error::RuntimeMismatch.into());
        }
        if status.round != req.round {
            return Err(Error::RoundMismatch.into());
        }
        if status.threshold == 0 {
```
After
```rust
return Err(Error::RuntimeMismatch.into());
        }
        if status.next_handoff != req.handoff {
            return Err(Error::HandoffMismatch.into());
        }
        if status.threshold == 0 {
```

## Snippet 4

Context: `go/worker/keymanager/churp.go:251` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// Stop and remove submission for the previous round.
	info, ok := s.submissions[status.ID]
	if ok && info.round < status.Round {
		removeFn(info, fmt.Errorf("new round"))
	}
```
After
```go
}

	// Stop and remove submission for the previous handoff.
	info, ok := s.submissions[status.ID]
	if ok && info.handoff < status.NextHandoff {
		removeFn(info, fmt.Errorf("new handoff"))
	}
```

# Fix Pattern

Replace inconsistent use of a related state field with one canonical protocol identifier across validation, persistence, and scheduling paths.

## How It Was Fixed

The patch updates both Go and Rust CHURP code so that requests are checked against the scheduled handoff epoch, persisted dealer material is loaded by handoff, and worker cleanup logic tracks handoff advancement instead of round advancement.

# Why It Matters

1. It makes multiple CHURP components use the same identifier for the same workflow.

2. It reduces the chance of local state or queued work being associated with the wrong handoff instance.

3. It looks like a correctness/protocol-alignment change, but the evidence here does not establish a concrete attack or security break.

# Evidence Notes

The strongest evidence is the direct replacement of `round` with `handoff`/`next_handoff` in four changed paths. The surrounding consensus code already refers to `status.NextHandoff`, which supports the inference that handoff is the intended coordinate. However, the supplied diff does not show type definitions, prior semantics of `status.Round`, or a failing scenario demonstrating replay, unauthorized action, secret exposure, or consensus failure. That makes stronger security claims unsupported from the provided evidence alone. Protocol security invariant: CHURP request validation, persisted handoff-specific dealer state, and submission scheduling should all use the same canonical handoff epoch identifier. The diff supports that consistency invariant, but does not by itself establish a concrete security failure from the prior `round`-based behavior. Verification notes: The patch does not prove an attacker could forge signatures, bypass authentication, or submit an otherwise invalid CHURP message. The patch does not prove secret key disclosure, threshold breakage, or compromise of enclave secrecy. The patch does not show a demonstrated on-chain consensus split; it shows correction of state binding in a consensus-critical protocol path. The exact exploitability of the old `round`-based behavior is not established from the diff alone. The patch clearly shows a consistency fix, not a demonstrated exploit. No provided evidence shows that old `round` values could be attacker-controlled or diverge from handoff in a security-relevant way. Tests were changed in the commit, but their contents/results are not provided here, so they cannot substantiate a vulnerability claim. The safest classification from this evidence is `unclear`, not a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-state-confusion`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `consensus, keymanager, churp, cryptographic-protocol, epoch-handoff`

The patch consistently rebinding CHURP logic from `round` to the canonical `handoff`/`next_handoff` field affects signed request validation, dealer state reuse across restarts, and stale submission handling in a keymanager consensus path. That is security-sensitive protocol hardening because it removes a risky state-coordinate mismatch in a cryptographic handoff workflow. However, the supplied evidence does not prove a concrete exploitable vulnerability, attacker-controlled bypass, or demonstrated confidentiality/integrity failure, so this is better retained as `security-hardening` rather than a confirmed `security-fix`.

## Security Evidence

1. Consensus-side CHURP application validation now checks `req.Application.Handoff` against `status.NextHandoff` instead of comparing `round` fields.
2. Runtime `init` validation now rejects requests unless `status.next_handoff == req.handoff`, tightening the binding before producing a signed application request.
3. Dealer/polynomial lookup on restart is now keyed by `handoff`, and the comment explicitly frames this as ensuring only one secret polynomial is generated per handoff unless a malicious host cleared storage.
4. Worker scheduling now retires old submissions based on handoff advancement, reducing stale cross-handoff work in the same protocol flow.

## Missing Evidence

1. No proof that the old `round` field could be attacker-controlled or used to bypass authentication or authorization.
2. No demonstrated replay, consensus split, secret disclosure, or threshold break caused by the prior behavior.
3. No commit message, advisory, or test result explicitly describing a security vulnerability or exploit scenario.

## Claim Boundaries

1. The evidence supports a security-sensitive protocol hardening around correct epoch/handoff binding in CHURP.
2. The patch alone does not prove a concrete exploitable bug, only that prior state binding was inconsistent.
3. The evidence does not establish signature forgery, access-control bypass, or confirmed confidentiality impact.
