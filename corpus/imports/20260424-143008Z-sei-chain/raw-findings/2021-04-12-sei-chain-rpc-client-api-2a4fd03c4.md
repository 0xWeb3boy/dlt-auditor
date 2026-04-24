---
case_id: case_20210412_2a4fd03c4
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: medium
date: 2021-04-12
source_refs:
  - git:2a4fd03c45ce3da4c963645797f47d44be0e7ba9
  - "sei-ibc-go/modules/core/keeper/msg_server.go:444"
  - "sei-ibc-go/modules/core/05-port/types/module.go:60"
  - "sei-ibc-go/modules/apps/transfer/module.go:318"
  - "sei-ibc-go/testing/mock/mock.go:175"
bug_class: failed-ack-state-rollback
impact_type:
  - state-consistency
  - protocol-invariant-enforcement
confidence: medium
tags:
  - ibc
  - packet-receive
  - acknowledgement
  - state-rollback
  - protocol-state
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes IBC packet receive handling so `OnRecvPacket` runs in a cached SDK context and its application-side state changes are written only when the acknowledgement is nil/asynchronous or successful. This is well supported as a protocol state-consistency and rollback fix. The provided evidence does not establish exploitability, attacker control, proof bypass, replay, authentication failure, or concrete economic impact, so it should not be classified as a confirmed or likely security fix.

## Observed Patch Facts

1. In `sei-ibc-go/modules/core/keeper/msg_server.go`, the patch replaces `_, ack, err := cbs.OnRecvPacket(ctx, msg.Packet)` with `// Cache context so that we may discard state changes from callback if the acknowledg...`.

2. In `sei-ibc-go/modules/core/05-port/types/module.go`, the patch replaces `// OnRecvPacket must return the acknowledgement bytes` with `// OnRecvPacket must return an acknowledgement that implements the Acknowledgement in...`.

3. In `sei-ibc-go/modules/apps/transfer/module.go`, the patch replaces `// OnRecvPacket implements the IBCModule interface` with `// OnRecvPacket implements the IBCModule interface. A successful acknowledgement`.

4. In `sei-ibc-go/testing/mock/mock.go`, the patch replaces `func (am AppModule) OnRecvPacket(sdk.Context, channeltypes.Packet) (*sdk.Result, []by...` with `func (am AppModule) OnRecvPacket(ctx sdk.Context, packet channeltypes.Packet) exporte...`.

## Project Context

The changed code sits primarily in `sei-ibc-go/modules/core/keeper`, `sei-ibc-go/modules/core`, `sei-ibc-go/modules/core/05-port/types`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `sei-ibc-go/modules/core/keeper/msg_server_test.go`, `sei-ibc-go/modules/core/04-channel/keeper/packet.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-ibc-go/modules/core/keeper/msg_server_test.go`, `sei-ibc-go/modules/core/exported/channel.go`. The strongest project-level identifiers around this patch are `OnRecvPacket`, `packet`, `acknowledgement`, and `Packet`.

## Before/After Behavior

Before the patch, `RecvPacket` invoked `cbs.OnRecvPacket(ctx, msg.Packet)` directly on the live context and received acknowledgement bytes plus an error. The supplied snippets do not show a transactional boundary around application callback writes. After the patch, `RecvPacket` creates `cacheCtx, writeFn := ctx.CacheContext()`, invokes `ack := cbs.OnRecvPacket(cacheCtx, msg.Packet)`, and calls `writeFn()` only for `ack == nil || ack.Success()`. The `IBCModule` interface documentation is updated to state that failed acknowledgements discard callback state while packet receipt and acknowledgement handling still proceed.

# Root Cause

The callback contract and core receive path did not tie application callback state commits to acknowledgement success. Application receive logic could mutate state before returning a failed synchronous acknowledgement, and the core path lacked the cached-context gate needed to discard those mutations.

## Walkthrough

1. `RecvPacket` performs module lookup, route lookup, and packet verification before invoking application receive logic.

2. Before the change, the callback was invoked on the main SDK context and returned acknowledgement bytes plus an error.

3. The patch invokes the callback using `ctx.CacheContext()`, staging application-side writes.

4. The returned acknowledgement object is then inspected by the core handler.

5. If the acknowledgement is nil, the handler treats it as asynchronous and commits the staged writes.

6. If the acknowledgement is successful, the handler commits the staged writes.

7. If the acknowledgement is a synchronous error acknowledgement, the handler does not call `writeFn()`, so callback mutations are discarded.

8. Transfer and mock modules are updated to return acknowledgement objects under the new interface.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-ibc-go/modules/core/keeper/msg_server.go | 444 | Core RecvPacket handler enforces cached application callback execution and commits callback state only for async or successful acknowledgements. |
| sei-ibc-go/modules/core/05-port/types/module.go | 60 | IBCModule OnRecvPacket contract defines acknowledgement semantics and failed-ack state discard behavior. |
| sei-ibc-go/modules/apps/transfer/module.go | 318 | ICS-20 transfer receive callback now returns success or error acknowledgements under the updated contract. |
| sei-ibc-go/testing/mock/mock.go | 175 | Mock application records canary state and returns success, async, or failed acknowledgements to test rollback behavior. |

## Code Snippets

## Snippet 1

Context: `sei-ibc-go/modules/core/keeper/msg_server.go:444` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Perform application logic callback
	_, ack, err := cbs.OnRecvPacket(ctx, msg.Packet)
	if err != nil {
		return nil, sdkerrors.Wrap(err, "receive packet callback failed")
	}
```
After
```go
// Perform application logic callback
	// Cache context so that we may discard state changes from callback if the acknowledgement is unsuccessful.
	cacheCtx, writeFn := ctx.CacheContext()
	ack := cbs.OnRecvPacket(cacheCtx, msg.Packet)
	if ack == nil || ack.Success() {
		// write application state changes for asynchronous and successful acknowledgements
		writeFn()
```

## Snippet 2

Context: `sei-ibc-go/modules/core/05-port/types/module.go:60` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
) error

	// OnRecvPacket must return the acknowledgement bytes
	// In the case of an asynchronous acknowledgement, nil should be returned.
	OnRecvPacket(
		ctx sdk.Context,
		packet channeltypes.Packet,
	) (*sdk.Result, []byte, error)
```
After
```go
) error

	// OnRecvPacket must return an acknowledgement that implements the Acknowledgement interface.
	// In the case of an asynchronous acknowledgement, nil should be returned.
	// If the acknowledgement returned is successful, the state changes on callback are written,
	// otherwise the application state changes are discarded. In either case the packet is received
	// and the acknowledgement is written (in synchronous cases).
	OnRecvPacket(
```

## Snippet 3

Context: `sei-ibc-go/modules/apps/transfer/module.go:318` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// OnRecvPacket implements the IBCModule interface
func (am AppModule) OnRecvPacket(
	ctx sdk.Context,
	packet channeltypes.Packet,
) (*sdk.Result, []byte, error) {
	var data types.FungibleTokenPacketData
```
After
```go
}

// OnRecvPacket implements the IBCModule interface. A successful acknowledgement
// is returned if the packet data is succesfully decoded and the receive application
// logic returns without error.
func (am AppModule) OnRecvPacket(
	ctx sdk.Context,
	packet channeltypes.Packet,
```

## Snippet 4

Context: `sei-ibc-go/testing/mock/mock.go:175` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// OnRecvPacket implements the IBCModule interface.
func (am AppModule) OnRecvPacket(sdk.Context, channeltypes.Packet) (*sdk.Result, []byte, error) {
	return nil, MockAcknowledgement, nil
}
```
After
```go
// OnRecvPacket implements the IBCModule interface.
func (am AppModule) OnRecvPacket(ctx sdk.Context, packet channeltypes.Packet) exported.Acknowledgement {
	// set state by claiming capability to check if revert happens return
	am.scopedKeeper.NewCapability(ctx, MockCanaryCapabilityName)
	if bytes.Equal(MockPacketData, packet.GetData()) {
		return MockAcknowledgement
	} else if bytes.Equal(MockAsyncPacketData, packet.GetData()) {
```

# Fix Pattern

Run application callbacks in a cached or transactional context, then commit callback mutations only after checking the protocol-level success signal.

## How It Was Fixed

`RecvPacket` now wraps `OnRecvPacket` execution in `ctx.CacheContext()`. The callback signature changes from returning `(*sdk.Result, []byte, error)` to returning an `exported.Acknowledgement`. The core handler writes cached state only for asynchronous or successful acknowledgements, and interface comments document the failed-ack rollback rule.

# Why It Matters

1. Prevents failed synchronous acknowledgements from committing application callback mutations.

2. Clarifies the distinction between packet receipt, acknowledgement writing, and application state commits.

3. Improves protocol state consistency for IBC receive handling.

4. Does not, from the supplied evidence, prove a concrete vulnerability or exploit path.

# Evidence Notes

The strongest evidence is in `sei-ibc-go/modules/core/keeper/msg_server.go`, where `ctx.CacheContext()` and conditional `writeFn()` are introduced. The interface contract in `sei-ibc-go/modules/core/05-port/types/module.go` explicitly states that failed acknowledgements discard callback state. Supporting transfer and mock changes show adaptation to the new acknowledgement-returning contract and rollback tests. Claims about RPC serialization, cryptographic failure, replay, authentication bypass, proof bypass, or demonstrated economic loss are unsupported by the provided evidence. Protocol security invariant: For IBC packet receipt, application callback state changes should not be committed when a synchronous acknowledgement reports failure; asynchronous and successful acknowledgements may commit callback state under the updated contract. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show a cryptographic verification failure. The patch does not establish replay, authentication, or proof-bypass behavior. The exact economic impact is not proven from the provided diff. The evidence shows rollback of callback mutations on failed acknowledgements, not a broad transaction rollback bug. Behavioral rollback change is directly supported by the provided diff snippets. Security impact is plausible but not established by the supplied evidence. No attacker model or exploitability path is shown. No concrete asset loss, privilege escalation, or consensus failure is demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `failed-ack-state-rollback`
Final impact type: `state-consistency, protocol-invariant-enforcement`
Final confidence: `medium`
Final tags: `ibc, packet-receive, acknowledgement, state-rollback, protocol-state`

The supplied patch clearly changes a security-sensitive IBC packet receive path so application callback writes are staged and only committed for successful or asynchronous acknowledgements. That supports retaining this as security hardening: it enforces a protocol state invariant and removes the risky condition where failed acknowledgements could leave application state mutations behind. The evidence does not prove a concrete exploit, asset loss, auth bypass, replay, or cryptographic failure, so it should not be upgraded to a confirmed security fix.

## Security Evidence

1. RecvPacket now executes OnRecvPacket inside ctx.CacheContext() instead of the live context.
2. Cached callback writes are committed only when ack is nil/asynchronous or ack.Success() is true.
3. The IBCModule contract explicitly says failed acknowledgements discard callback state changes.
4. Mock test code adds a canary state mutation to verify failed-ack rollback behavior.
5. The changed path handles verified IBC packet receipt and acknowledgement processing, a protocol-critical state transition.

## Missing Evidence

1. No attacker model or malicious packet flow is shown.
2. No concrete exploit path or proof of remote triggerability is provided.
3. No demonstrated asset loss, privilege escalation, consensus failure, replay, or proof bypass is shown.
4. No evidence shows which real application callbacks could mutate state before returning a failed acknowledgement.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Limit the claim to failed synchronous acknowledgement rollback of application callback state.
3. Do not describe this as an RPC client API serialization issue.
4. Do not claim cryptographic verification, replay protection, authentication, or economic loss impacts from the supplied evidence alone.
