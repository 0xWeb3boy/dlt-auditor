---
case_id: case_20220202_a613471d8
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: high
date: 2022-02-02
source_refs:
  - git:a613471d88983aa1db304ac09e9dae6ae8ca97f0
  - "sei-ibc-go/modules/core/04-channel/types/acknowledgement.go:21"
  - "sei-ibc-go/modules/apps/27-interchain-accounts/host/types/ack.go:15"
  - "sei-ibc-go/modules/apps/transfer/ibc_module.go:182"
  - "sei-ibc-go/modules/apps/transfer/types/ack_test.go:1"
bug_class: consensus-determinism
impact_type:
  - state-consistency
  - consensus-divergence
confidence: medium
tags:
  - blockchain-core
  - ibc
  - acknowledgement
  - consensus-determinism
  - state-consistency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for consensus determinism in IBC transfer error acknowledgements. The patch changes the transfer receive failure path from committing `err.Error()` directly into an acknowledgement to using a transfer-specific acknowledgement helper, and adds documentation warning that acknowledgement error strings are written into state and can cause app hash divergence across mixed patch versions.

## Observed Patch Facts

1. In `sei-ibc-go/modules/core/04-channel/types/acknowledgement.go`, the patch adds `// NOTE: Acknowledgements are written into state and thus, changes made to error stri...`.

2. In `sei-ibc-go/modules/apps/27-interchain-accounts/host/types/ack.go`, the patch replaces `// AcknowledgementErrorString returns a deterministic error string which may be used in` with `// NewErrorAcknowledgement returns a deterministic error string which may be used in`.

3. In `sei-ibc-go/modules/apps/transfer/ibc_module.go`, the patch replaces `ack = channeltypes.NewErrorAcknowledgement(err.Error())` with `ack = types.NewErrorAcknowledgement(err)`.

4. In `sei-ibc-go/modules/apps/transfer/types/ack_test.go`, the patch adds `sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"`.

## Project Context

The changed code sits primarily in `sei-ibc-go/modules/core/04-channel/types`, `sei-ibc-go/modules/core/04-channel`, `sei-ibc-go/modules/apps/27-interchain-accounts/host/types`, which anchors the finding in the `core-logic` area of the project. Historical context from `sei-ibc-go/modules/core/04-channel/types/acknowledgement_test.go`, `sei-ibc-go/modules/core/04-channel/types/errors.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-ibc-go/modules/apps/transfer/types/ack.go`, `sei-ibc-go/modules/apps/27-interchain-accounts/host/types/ack_test.go`. The strongest project-level identifiers around this patch are `NewErrorAcknowledgement`, `tendermint`, `Acknowledgement`, and `error`.

## Before/After Behavior

Before the patch, `IBCModule.OnRecvPacket` used `channeltypes.NewErrorAcknowledgement(err.Error())` when `im.keeper.OnRecvPacket` failed, placing the raw runtime error string into the acknowledgement. After the patch, that path calls `types.NewErrorAcknowledgement(err)`, which is supported by transfer acknowledgement helper code with a stable error string constant. The core acknowledgement godoc was updated to warn that acknowledgement error strings are state-machine relevant.

# Root Cause

The supported root cause is use of raw error text in a consensus-committed IBC acknowledgement on the transfer receive error path. Because error text can change across versions or formatting paths, committing it can create divergent acknowledgement bytes for the same logical failure. The evidence supports an app-hash-divergence risk, but does not establish packet forgery, fund theft, authorization bypass, or cryptographic verification failure.

## Walkthrough

1. Transfer `OnRecvPacket` initializes a success acknowledgement and decodes packet data.

2. If transfer application logic returns an error, the pre-patch code built the acknowledgement from `err.Error()`.

3. Acknowledgements are written into state, according to the added core channel warning.

4. The patch routes the keeper error through `types.NewErrorAcknowledgement(err)` instead of directly committing the raw error string.

5. The transfer helper context shows a stable `ackErrorString` constant documented as state-machine breaking if changed.

6. Added tests and related ICA helper context support that the intended behavior is deterministic acknowledgement construction.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-ibc-go/modules/apps/transfer/ibc_module.go | 182 | Transfer `OnRecvPacket` error path now emits deterministic transfer error acknowledgement instead of raw `err.Error()`. |
| sei-ibc-go/modules/apps/transfer/types/ack.go | 1 | Defines transfer acknowledgement error constant and deterministic error acknowledgement construction using ABCI error code information. |
| sei-ibc-go/modules/core/04-channel/types/acknowledgement.go | 21 | Documents consensus-state risk of changing acknowledgement error strings because acknowledgements are written into state. |
| sei-ibc-go/modules/apps/transfer/types/ack_test.go | 1 | Adds tests covering deterministic acknowledgement behavior against Tendermint/ABCI hashing context. |
| sei-ibc-go/modules/apps/27-interchain-accounts/host/types/ack.go | 15 | Parallel deterministic acknowledgement helper and documentation baseline used as reference for transfer behavior. |

## Code Snippets

## Snippet 1

Context: `sei-ibc-go/modules/core/04-channel/types/acknowledgement.go:21` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// NewErrorAcknowledgement returns a new instance of Acknowledgement using an Acknowledgement_Error
// type in the Response field.
func NewErrorAcknowledgement(err string) Acknowledgement {
	return Acknowledgement{
```
After
```go
// NewErrorAcknowledgement returns a new instance of Acknowledgement using an Acknowledgement_Error
// type in the Response field.
// NOTE: Acknowledgements are written into state and thus, changes made to error strings included in packet acknowledgements
// risk an app hash divergence when nodes in a network are running different patch versions of software.
func NewErrorAcknowledgement(err string) Acknowledgement {
	return Acknowledgement{
```

## Snippet 2

Context: `sei-ibc-go/modules/apps/27-interchain-accounts/host/types/ack.go:15` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
)

// AcknowledgementErrorString returns a deterministic error string which may be used in
// the packet acknowledgement.
func NewErrorAcknowledgement(err error) channeltypes.Acknowledgement {
	// the ABCI code is included in the abcitypes.ResponseDeliverTx hash
	// constructed in Tendermint and is therefore determinstic
	_, code, _ := sdkerrors.ABCIInfo(err, false) // discard non-determinstic codespace and log values
```
After
```go
)

// NewErrorAcknowledgement returns a deterministic error string which may be used in
// the packet acknowledgement.
func NewErrorAcknowledgement(err error) channeltypes.Acknowledgement {
	// the ABCI code is included in the abcitypes.ResponseDeliverTx hash
	// constructed in Tendermint and is therefore determinstic
	_, code, _ := sdkerrors.ABCIInfo(err, false) // discard non-deterministic codespace and log values
```

## Snippet 3

Context: `sei-ibc-go/modules/apps/transfer/ibc_module.go:182` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
err := im.keeper.OnRecvPacket(ctx, packet, data)
		if err != nil {
			ack = channeltypes.NewErrorAcknowledgement(err.Error())
		}
	}
```
After
```go
err := im.keeper.OnRecvPacket(ctx, packet, data)
		if err != nil {
			ack = types.NewErrorAcknowledgement(err)
		}
	}
```

## Snippet 4

Context: `sei-ibc-go/modules/apps/transfer/types/ack_test.go:1` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
(no before snippet captured)
```
After
```go
package types_test

import (
	"testing"

	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
	"github.com/stretchr/testify/suite"
	abcitypes "github.com/tendermint/tendermint/abci/types"
```

# Fix Pattern

Replace raw error-string acknowledgement serialization in consensus state with a module-level deterministic acknowledgement constructor backed by stable acknowledgement text and deterministic error metadata where applicable.

## How It Was Fixed

The transfer receive error path was changed from `channeltypes.NewErrorAcknowledgement(err.Error())` to `types.NewErrorAcknowledgement(err)`. Transfer acknowledgement support code defines a stable acknowledgement error string, and the core channel acknowledgement documentation now warns that changing error strings in acknowledgements can cause app hash divergence.

# Why It Matters

1. IBC acknowledgements are consensus-state data.

2. Consensus nodes must commit identical acknowledgement bytes for the same packet result.

3. Raw error strings can vary across versions or formatting paths.

4. Divergent acknowledgement bytes can risk app hash divergence.

5. The evidence supports consensus determinism impact, not direct asset theft or packet forgery.

# Evidence Notes

Primary evidence is the changed line in `sei-ibc-go/modules/apps/transfer/ibc_module.go` replacing `channeltypes.NewErrorAcknowledgement(err.Error())` with `types.NewErrorAcknowledgement(err)`. Supporting evidence is the transfer `ack.go` context showing a stable `ackErrorString` constant and comments that changing it is state-machine breaking. The strongest explanatory evidence is the added core channel comment stating that acknowledgements are written into state and changed error strings can risk app hash divergence. Claims about exploitability, fund loss, packet forgery, or cryptographic failure are unsupported. The full transfer helper body is not shown in the provided snippets, so details about exact ABCI-code formatting should be treated as supporting context rather than the core finding. Protocol security invariant: IBC packet acknowledgements are written into consensus state, so nodes processing the same packet outcome must derive identical acknowledgement bytes. Error acknowledgement payloads should not depend on raw runtime error text that may vary across software versions or formatting. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show funds can be stolen or packets forged. The patch does not change cryptographic verification logic. The patch does not prove an active chain halt occurred, only that divergent acknowledgement bytes could risk app hash divergence. The evidence supports consensus determinism impact, not an application authorization bypass. Verified from provided input only; no repository inspection was performed. Security relevance is based on consensus determinism and app-hash-divergence risk stated in the patch comments. Confidence is medium because the evidence establishes the risky pattern and fix direction, but not an observed exploit or full helper implementation details. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-determinism`
Final impact type: `state-consistency, consensus-divergence`
Final confidence: `medium`
Final tags: `blockchain-core, ibc, acknowledgement, consensus-determinism, state-consistency`

The patch clearly moves an IBC transfer receive error acknowledgement away from raw err.Error() and toward a deterministic module helper backed by stable acknowledgement text, with comments explicitly warning that acknowledgement error strings are written into state and can cause app hash divergence across mixed versions. That supports security hardening for blockchain consensus determinism, but the supplied evidence does not prove an exploitable vulnerability, active incident, fund loss, authorization bypass, or cryptographic failure, so security-fix is too strong.

## Security Evidence

1. Transfer OnRecvPacket changed from channeltypes.NewErrorAcknowledgement(err.Error()) to types.NewErrorAcknowledgement(err).
2. Core acknowledgement comment states acknowledgement error strings are written into state and can risk app hash divergence.
3. Transfer ack context defines a stable ackErrorString and warns that changing it is state-machine breaking.
4. Helper comments describe deterministic acknowledgement construction and discarding non-deterministic error information.

## Missing Evidence

1. No evidence of a concrete exploit path or attacker-controlled trigger causing divergence.
2. No evidence of fund theft, packet forgery, authorization bypass, or cryptographic verification failure.
3. No full before/after helper body is supplied for all transfer acknowledgement behavior.
4. No incident report or security advisory metadata is provided.

## Claim Boundaries

1. Keep claims limited to consensus determinism and state consistency hardening.
2. Do not claim direct asset loss, packet forgery, or authentication bypass.
3. Do not classify as a proven security-fix from the patch alone.
4. The supported risk is app-hash or consensus divergence from non-stable acknowledgement error strings.
