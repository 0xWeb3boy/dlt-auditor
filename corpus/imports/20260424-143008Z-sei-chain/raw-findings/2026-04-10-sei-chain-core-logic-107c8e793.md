---
case_id: case_20260410_107c8e793
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2026-04-10
source_refs:
  - git:107c8e79396b1cdd735bd7e18946b0cd55f92537
  - "sei-tendermint/internal/p2p/mux/mux.go:125"
  - "sei-tendermint/internal/p2p/mux/mux_test.go:632"
  - "sei-tendermint/internal/p2p/mux/stream_state.go:62"
  - "sei-tendermint/internal/p2p/mux/stream_state.go:78"
bug_class: protocol-validation-hardening
impact_type:
  - resource-limit-enforcement
  - protocol-state-integrity
confidence: medium
tags:
  - p2p
  - mux
  - protocol-validation
  - stream-kind
  - resource-limits
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens p2p mux stream-kind validation: missing kind on new inbound stream creation is rejected, and explicit kind mismatch on an existing stream now returns an error. This is plausibly security relevant because kind participates in inbound accept-limit handling, but the provided evidence does not demonstrate an exploit, resource-limit bypass, privilege boundary, consensus impact, or other concrete vulnerability.

## Observed Patch Facts

1. In `sei-tendermint/internal/p2p/mux/mux.go`, the patch replaces `// getOrAccept() gets the current state of the stream with the given id (kind is igno...` with `// getOrAccept() gets the current state of the stream for the given header message.`.

2. In `sei-tendermint/internal/p2p/mux/mux_test.go`, the patch adds `func TestProtocol_OpenWithoutKind(t *testing.T) {`.

3. In `sei-tendermint/internal/p2p/mux/stream_state.go`, the patch replaces `return fmt.Errorf("already opened")` with `return errAlreadyOpened`.

4. In `sei-tendermint/internal/p2p/mux/stream_state.go`, the patch replaces `return fmt.Errorf("already closed")` with `return errAlreadyClosed`.

## Project Context

The changed code sits primarily in `sei-tendermint/internal/p2p/mux`, `sei-tendermint/internal/p2p`, which anchors the finding in the `core-logic` area of the project. Historical context from `sei-tendermint/internal/p2p/mux/stream.go`, `sei-tendermint/internal/p2p/rpc/rpc.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/internal/p2p/mux/stream.go`, `sei-tendermint/internal/p2p/rpc/rpc.go`. The strongest project-level identifiers around this patch are `inner`, `kind`, `stream`, and `getOrAccept`.

## Before/After Behavior

Before the change, getOrAccept accepted a stream id and kind separately, and its comment stated that kind was ignored for existing stream lookup. A missing kind could be read through GetKind as the zero value, as reflected by the new test comment. After the change, getOrAccept receives the full header, derives id and kind internally, rejects new inbound stream creation when h.Kind is nil, and rejects explicit kind mismatch for an existing stream.

# Root Cause

The mux header handling path under-validated the stream-kind field: existing stream lookup did not reject kind disagreement, and new stream handling could proceed from a defaulted kind when the header omitted the field.

## Walkthrough

1. A peer sends a mux header for a remote stream id into getOrAccept.

2. Before the patch, existing stream lookup was by id and the visible comment said kind was ignored.

3. If the stream did not exist, the inbound creation path used a StreamKind value derived outside getOrAccept, and the new test indicates a missing kind could default to 0.

4. The patch makes getOrAccept inspect the full header directly.

5. For existing streams, an explicit header kind that differs from the stored stream kind now returns errStreamKindMismatch.

6. For new inbound streams, h.Kind == nil now returns errUnknownStream instead of accepting a default kind.

7. The stream_state.go changes replace ad hoc duplicate open/close errors with named errors and are support cleanup, not an independent vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/internal/p2p/mux/mux.go | 125 | Inbound header handling for remote stream lookup or accept; now enforces explicit kind on new remote stream creation and detects kind mismatch on existing streams. |
| sei-tendermint/internal/p2p/mux/mux_test.go | 632 | Regression test for rejecting an OPEN frame with no kind instead of defaulting it to stream kind 0. |
| sei-tendermint/internal/p2p/mux/mux_test.go | 603 | Adjacent protocol test context showing unknown kinds interact with inbound accept limits. |
| sei-tendermint/internal/p2p/mux/stream_state.go | 62 | RemoteOpen duplicate-open error normalization; secondary to the kind-validation fix. |
| sei-tendermint/internal/p2p/mux/stream_state.go | 78 | RemoteClose duplicate-close error normalization; secondary cleanup for protocol-state errors. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/internal/p2p/mux/mux.go:125` (changes a sensitive control or state-update path)

Before
```go
}

// getOrAccept() gets the current state of the stream with the given id (kind is ignored).
// If the stream does not exist yet, it tries to create it as an accept (inbound) stream.
// In that case the inbound stream limit for the given kind is checked.
func (r *runner) getOrAccept(id streamID, kind StreamKind) (*streamState, error) {
	for inner := range r.inner.RLock() {
		s, ok := inner.streams[id]
```
After
```go
}

// getOrAccept() gets the current state of the stream for the given header message.
// If the stream does not exist yet, it tries to create it as an accept (inbound) stream.
// In that case the inbound stream limit for the given kind is checked.
func (r *runner) getOrAccept(h *pb.Header) (*streamState, error) {
	id := streamIDFromRemote(h.Id)
	kind := StreamKind(h.GetKind())
```

## Snippet 2

Context: `sei-tendermint/internal/p2p/mux/mux_test.go:632` (changes bounds, limits, or capacity handling)

Before
```go
}
}
```
After
```go
}
}

func TestProtocol_OpenWithoutKind(t *testing.T) {
	err := scope.Run(t.Context(), func(ctx context.Context, s scope.Scope) error {
		c1, c2 := conn.NewTestConn()
		kind := StreamKind(0)
```

## Snippet 3

Context: `sei-tendermint/internal/p2p/mux/stream_state.go:62` (changes a sensitive control or state-update path)

Before
```go
for inner, ctrl := range s.inner.Lock() {
		if inner.send.remoteOpened {
			return fmt.Errorf("already opened")
		}
		// Do not allow remote open before we connect.
```
After
```go
for inner, ctrl := range s.inner.Lock() {
		if inner.send.remoteOpened {
			return errAlreadyOpened
		}
		// Do not allow remote open before we connect.
```

## Snippet 4

Context: `sei-tendermint/internal/p2p/mux/stream_state.go:78` (changes a sensitive control or state-update path)

Before
```go
for inner, ctrl := range s.inner.Lock() {
		if inner.closed.remote {
			return fmt.Errorf("already closed")
		}
		inner.closed.remote = true
```
After
```go
for inner, ctrl := range s.inner.Lock() {
		if inner.closed.remote {
			return errAlreadyClosed
		}
		inner.closed.remote = true
```

# Fix Pattern

Tighten protocol boundary validation by requiring explicit discriminator fields on creation and checking discriminator consistency against stored stream state.

## How It Was Fixed

mux.go changed getOrAccept to accept *pb.Header, derive the remote stream id and kind internally, reject missing kind for new inbound streams, and return errStreamKindMismatch for explicit kind disagreement on existing streams. mux_test.go adds regression coverage for OPEN without kind. stream_state.go normalizes duplicate open/close errors to named sentinel errors.

# Why It Matters

1. Prevents silent defaulting of missing stream kind to kind 0.

2. Makes stream-kind consistency explicit in the mux state machine.

3. Supports cleaner inbound accept-limit enforcement by requiring explicit kind data.

4. Security impact remains unproven from the supplied evidence.

# Evidence Notes

The strongest evidence is the getOrAccept change in mux.go and the new TestProtocol_OpenWithoutKind in mux_test.go. Adjacent test context supports that unknown kinds interact with inbound accept limits. Related rpc.go context shows RPCs have Kind and Limit fields, but this only supports a cautious inference about classification and limits. The evidence does not prove a concrete attack path or that the old behavior bypassed meaningful security controls. Protocol security invariant: Inbound mux stream creation should include an explicit stream kind, and later headers that explicitly name a kind should not conflict with the stream state's stored kind. The evidence shows this is enforced for protocol correctness and inbound accept-limit selection, but does not establish a concrete security impact. Verification notes: No direct exploit path is demonstrated in the supplied patch evidence. No authentication, cryptographic, or consensus-safety break is shown by the patch alone. No proof is provided that kind mismatch bypasses all resource limits, only that kind is used in inbound accept-limit handling. The stream_state.go changes look like error normalization and are not independently security-relevant. No concrete exploit path is shown. No authentication, cryptographic, consensus, or authorization impact is shown. No proof is provided that kind mismatch bypassed resource limits in practice. The patch is best treated as protocol validation hardening with unclear security significance. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-validation-hardening`
Final impact type: `resource-limit-enforcement, protocol-state-integrity`
Final confidence: `medium`
Final tags: `p2p, mux, protocol-validation, stream-kind, resource-limits`

The evidence supports retaining this as security hardening, not a proven vulnerability fix. The patch tightens validation on a peer-controlled p2p mux header by requiring an explicit stream kind for new inbound streams and rejecting explicit kind mismatches against existing stream state. Because stream kind participates in inbound accept-limit selection, this is security-relevant boundary hardening, but the supplied evidence does not prove a concrete exploit, denial-of-service path, consensus impact, or authorization bypass.

## Security Evidence

1. P2P mux header handling now receives the full header and validates the stream kind field directly.
2. New inbound stream creation rejects missing h.Kind instead of allowing GetKind to default to stream kind 0.
3. Existing streams now reject explicit kind mismatches with errStreamKindMismatch instead of ignoring kind.
4. Adjacent test evidence states unknown kinds are treated as having zero allowed accepts, tying kind to inbound accept-limit behavior.
5. A new regression test covers OPEN frames without kind and expects rejection.

## Missing Evidence

1. No demonstrated exploit path or attacker workflow is provided.
2. No proof shows the prior default-to-zero behavior bypassed meaningful resource limits in practice.
3. No concrete denial-of-service, consensus, authentication, authorization, or cryptographic impact is shown.
4. The stream_state.go sentinel error changes appear to be cleanup rather than independently security-relevant.

## Claim Boundaries

1. Classify as protocol validation hardening, not a confirmed security fix.
2. Do not claim a proven resource-exhaustion vulnerability from the supplied patch alone.
3. Do not claim consensus safety impact or privilege escalation.
4. The supported claim is limited to stricter validation of peer-controlled mux stream kind data and better enforcement of stream-kind consistency.
