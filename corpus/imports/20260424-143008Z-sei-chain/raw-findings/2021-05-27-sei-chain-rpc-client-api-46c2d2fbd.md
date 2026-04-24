---
case_id: case_20210527_46c2d2fbd
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: medium
date: 2021-05-27
source_refs:
  - git:46c2d2fbd5f38fa5c525581c18c8366ec5fb5052
  - "sei-ibc-go/modules/core/02-client/types/client.pb.go:1441"
  - "sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go:60"
  - "sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go:35"
  - "sei-ibc-go/modules/core/02-client/keeper/proposal.go:40"
bug_class: ibc-client-recovery-hardening
impact_type:
  - state-consistency
  - consensus-client-integrity
confidence: medium
tags:
  - ibc
  - client-recovery
  - consensus-state
  - governance-proposal
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch simplifies the IBC ClientUpdateProposal recovery path by removing the proposal-supplied InitialHeight flow, adding keeper-level checks that the substitute is active and ahead of the subject, and copying the substitute client's latest consensus state rather than iterating over a caller-influenced historical range. This is plausibly security-relevant hardening for IBC client recovery, but the provided evidence does not prove an exploitable vulnerability, so it should not be retained as a confirmed security fix.

## Observed Patch Facts

1. In `sei-ibc-go/modules/core/02-client/types/client.pb.go`, the patch replaces `case 5:` with `default:`.

2. In `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go`, the patch replaces `for i := initialHeight.GetRevisionHeight(); i <= substituteClientState.GetLatestHeigh...` with `height := substituteClientState.GetLatestHeight()`.

3. In `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go`, the patch replaces `// substitute clients are not allowed to be upgraded during the voting period` with `if !IsMatchingClientState(cs, *substituteClientState) {`.

4. In `sei-ibc-go/modules/core/02-client/keeper/proposal.go`, the patch replaces `clientState, err := subjectClientState.CheckSubstituteAndUpdateState(ctx, k.cdc, k.Cl...` with `if subjectClientState.GetLatestHeight().GTE(substituteClientState.GetLatestHeight()) {`.

## Project Context

The changed code sits primarily in `sei-ibc-go/modules/core/02-client/types`, `sei-ibc-go/modules/core/02-client`, `sei-ibc-go/modules/light-clients/07-tendermint/types`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle_test.go`, `sei-ibc-go/modules/light-clients/07-tendermint/types/client_state.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle_test.go`, `sei-ibc-go/modules/core/02-client/keeper/proposal_test.go`. The strongest project-level identifiers around this patch are `height`, `substituteClientState`, `GetLatestHeight`, and `substitute`.

## Before/After Behavior

Before the patch, ClientUpdateProposal passed InitialHeight into CheckSubstituteAndUpdateState. The Tendermint implementation checked revision-number consistency against that initial height, iterated from the initial revision height through the substitute latest revision height, copied available consensus states, and skipped missing ones. The generated decoder also handled the InitialHeight field. After the patch, the keeper rejects recovery when the subject latest height is greater than or equal to the substitute latest height, requires the substitute client to be Active, calls CheckSubstituteAndUpdateState without InitialHeight, and the Tendermint handler retrieves and copies only the substitute latest consensus state, returning an error if that state is unavailable. The decoder no longer decodes the removed InitialHeight field.

# Root Cause

The prior recovery design spread state-selection decisions across a proposal-provided InitialHeight and a Tendermint range-copy loop that tolerated missing historical consensus states. The patch removes that ambiguity by deriving the copied consensus state from the substitute client's latest height and enforcing substitute suitability at the keeper boundary. The evidence supports a consistency issue or cleanup in recovery semantics, not a demonstrated security flaw.

## Walkthrough

1. A governance ClientUpdateProposal enters the keeper, which loads the subject and substitute client states.

2. The patched keeper continues to reject localhost clients, missing clients, and active subject clients.

3. The patched keeper now rejects the proposal if the subject client's latest height is greater than or equal to the substitute client's latest height.

4. The patched keeper requires the substitute client status to be Active before invoking client-specific recovery logic.

5. The Tendermint recovery handler checks that the substitute client is a Tendermint ClientState and that it matches the subject client state.

6. The handler permits recovery only for Frozen or Expired subject clients subject to the existing allow-update flags.

7. The patched handler no longer uses a proposal-supplied InitialHeight or iterates through a range of historical consensus states.

8. The patched handler selects substituteClientState.GetLatestHeight(), retrieves that exact consensus state, and errors if it is missing.

9. The generated proposal decoder no longer has explicit InitialHeight decoding for ClientUpdateProposal.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-ibc-go/modules/core/02-client/keeper/proposal.go | 21 | governance proposal entry point; validates subject/substitute client existence, subject status, relative latest heights, substitute activity, and invokes the client-specific update |
| sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go | 26 | Tendermint client recovery logic; validates substitute type and matching client parameters, permits only frozen/expired recovery states, and copies substitute latest consensus state |
| sei-ibc-go/modules/core/02-client/types/client.pb.go | 1441 | proposal wire decoding; removes handling for the previous InitialHeight field and treats it as an unknown/removed field |

## Code Snippets

## Snippet 1

Context: `sei-ibc-go/modules/core/02-client/types/client.pb.go:1441` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
m.SubstituteClientId = string(dAtA[iNdEx:postIndex])
			iNdEx = postIndex
		case 5:
			if wireType != 2 {
				return fmt.Errorf("proto: wrong wireType = %d for field InitialHeight", wireType)
			}
			var msglen int
			for shift := uint(0); ; shift += 7 {
```
After
```go
m.SubstituteClientId = string(dAtA[iNdEx:postIndex])
			iNdEx = postIndex
		default:
			iNdEx = preIndex
```

## Snippet 2

Context: `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go:60` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// copy consensus states and processed time from substitute to subject
	// starting from initial height and ending on the latest height (inclusive)
	for i := initialHeight.GetRevisionHeight(); i <= substituteClientState.GetLatestHeight().GetRevisionHeight(); i++ {
		height := clienttypes.NewHeight(substituteClientState.GetLatestHeight().GetRevisionNumber(), i)

		consensusState, err := GetConsensusState(substituteClientStore, cdc, height)
		if err != nil {
			// not all consensus states will be filled in
```
After
```go
// copy consensus states and processed time from substitute to subject
	// starting from initial height and ending on the latest height (inclusive)
	height := substituteClientState.GetLatestHeight()

	consensusState, err := GetConsensusState(substituteClientStore, cdc, height)
	if err != nil {
		return nil, sdkerrors.Wrap(err, "unable to retrieve latest consensus state for substitute client")
	}
```

## Snippet 3

Context: `sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go:35` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// substitute clients are not allowed to be upgraded during the voting period
	// If an upgrade passes before the subject client has been updated, a new proposal must be created
	// with an initial height that contains the new revision number.
	if substituteClientState.GetLatestHeight().GetRevisionNumber() != initialHeight.GetRevisionNumber() {
		return nil, sdkerrors.Wrapf(
			clienttypes.ErrInvalidHeight, "substitute client revision number must equal initial height revision number (%d != %d)",
```
After
```go
}

	if !IsMatchingClientState(cs, *substituteClientState) {
		return nil, sdkerrors.Wrap(clienttypes.ErrInvalidSubstitute, "subject client state does not match substitute client state")
	}

	switch cs.Status(ctx, subjectClientStore, cdc) {
```

## Snippet 4

Context: `sei-ibc-go/modules/core/02-client/keeper/proposal.go:40` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	clientState, err := subjectClientState.CheckSubstituteAndUpdateState(ctx, k.cdc, k.ClientStore(ctx, p.SubjectClientId), k.ClientStore(ctx, p.SubstituteClientId), substituteClientState, p.InitialHeight)
	if err != nil {
		return err
```
After
```go
}

	if subjectClientState.GetLatestHeight().GTE(substituteClientState.GetLatestHeight()) {
		return sdkerrors.Wrapf(types.ErrInvalidHeight, "subject client state latest height is greater or equal to substitute client state latest height (%s >= %s)", subjectClientState.GetLatestHeight(), substituteClientState.GetLatestHeight())
	}

	substituteClientStore := k.ClientStore(ctx, p.SubstituteClientId)
```

# Fix Pattern

Remove caller-supplied recovery range selection, enforce substitute-client preconditions at the proposal entry point, and copy the substitute client's latest consensus state directly.

## How It Was Fixed

InitialHeight was removed from the proposal wire/API path and from the Tendermint recovery handler signature. The keeper added checks for a strictly newer substitute latest height and an Active substitute status. The Tendermint handler now uses substituteClientState.GetLatestHeight() directly and requires the corresponding consensus state to exist before updating the subject client.

# Why It Matters

1. IBC client recovery affects future verification behavior for the recovered client.

2. Using a single latest substitute consensus state is clearer than copying a sparse range selected through proposal input.

3. Active and newer-substitute checks make recovery preconditions explicit.

4. The evidence does not show unauthorized governance, forged proofs, packet forgery, or asset loss.

# Evidence Notes

Supported by diffs in sei-ibc-go/modules/core/02-client/keeper/proposal.go, sei-ibc-go/modules/light-clients/07-tendermint/types/proposal_handle.go, and sei-ibc-go/modules/core/02-client/types/client.pb.go. The mapper's subsystem is better grounded as ibc-client-recovery than rpc-client-api. However, the mapper's keep_in_security_corpus=true is not supported under an unclear security verdict. The patch may be security-relevant because IBC client state is security-sensitive, but the supplied evidence establishes recovery-flow simplification and consistency hardening only. Protocol security invariant: IBC client recovery should update a non-active subject client only from a compatible substitute client, with unambiguous consensus state selection for the recovered client. The supplied evidence shows the patch tightening that recovery flow, but does not establish a concrete vulnerability or exploit path. Verification notes: The patch does not prove an attacker could pass governance or submit an unauthorized recovery proposal. The patch does not show forged consensus proofs or validator-set compromise. The patch does not prove funds could be stolen or packets falsely verified. The evidence supports a recovery-state consistency hardening, not a confirmed exploit fix. Serialization changes are secondary to the client recovery business-logic path. No provided evidence proves exploitability. No provided evidence shows unauthorized proposal submission or governance bypass. No provided evidence shows forged consensus verification or packet acceptance. Treat generated protobuf changes as support for the removed InitialHeight field, not as the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ibc-client-recovery-hardening`
Final impact type: `state-consistency, consensus-client-integrity`
Final confidence: `medium`
Final tags: `ibc, client-recovery, consensus-state, governance-proposal, security-hardening`

The evidence does not prove a concrete exploit or unauthorized action, so this should not be treated as a confirmed security fix. However, the patch clearly tightens behavior in a security-sensitive IBC client recovery path by removing proposal-supplied recovery range selection, requiring an active and newer substitute client, and requiring the latest substitute consensus state to exist. That is enough to retain conservatively as security hardening rather than as a vulnerability fix.

## Security Evidence

1. IBC client recovery affects light-client state used for future verification behavior.
2. Keeper now rejects substitute clients that are not ahead of the subject client.
3. Keeper now requires the substitute client to be Active before recovery proceeds.
4. Tendermint recovery now copies the substitute latest consensus state directly and errors if it is missing.
5. The proposal InitialHeight field and caller-influenced historical range copy path were removed.

## Missing Evidence

1. No evidence of unauthorized governance proposal submission or governance bypass.
2. No proof that the prior InitialHeight behavior enabled forged packets, false consensus verification, or asset loss.
3. No advisory, CVE, exploit narrative, or explicit security statement is provided.
4. No evidence that skipped missing historical consensus states caused an exploitable condition.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim confirmed exploitability or fund loss.
3. Do not frame the protobuf decoder change as the primary security issue; it supports removal of InitialHeight.
4. Subsystem should be described as IBC client recovery rather than rpc-client-api.
