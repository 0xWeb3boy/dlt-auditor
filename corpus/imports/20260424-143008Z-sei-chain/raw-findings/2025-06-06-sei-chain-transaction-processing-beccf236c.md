---
case_id: case_20250606_beccf236c
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2025-06-06
source_refs:
  - git:beccf236cc3e5a4d636db09bb48098d55451aa72
  - "precompiles/gov/gov.go:128"
  - "precompiles/gov/gov.go:214"
  - "precompiles/gov/gov.go:81"
  - "precompiles/gov/gov_test.go:231"
bug_class: validation-bypass-hardening
impact_type:
  - governance-validation-divergence
confidence: medium
tags:
  - blockchain-core
  - evm-precompile
  - governance
  - message-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes gov precompile vote and deposit handling to construct Cosmos SDK governance messages, call ValidateBasic, and dispatch through the gov MsgServer instead of calling keeper methods directly. This is plausibly validation hardening, but the provided evidence does not establish a concrete vulnerability, accepted invalid payload, privilege bypass, fund loss, governance takeover, consensus failure, replay issue, or cryptographic flaw. The commit also appears to add missing governance precompile methods and tests, so it should not be retained as a confirmed security fix.

## Observed Patch Facts

1. In `precompiles/gov/gov.go`, the patch replaces `err := p.govKeeper.AddVote(ctx, proposalID, voter, govtypes.NewNonSplitVoteOption(gov...` with `msg := govtypes.NewMsgVote(voter, proposalID, govtypes.VoteOption(voteOption))`.

2. In `precompiles/gov/gov.go`, the patch replaces `res, err := p.govKeeper.AddDeposit(ctx, proposalID, depositor, sdk.NewCoins(coin))` with `msg := govtypes.NewMsgDeposit(depositor, proposalID, sdk.NewCoins(coin))`.

3. In `precompiles/gov/gov.go`, the patch replaces `if bytes.Equal(method.ID, p.VoteID) {` with `if bytes.Equal(method.ID, p.VoteID) || bytes.Equal(method.ID, p.VoteWeightedID) {`.

4. In `precompiles/gov/gov_test.go`, the patch replaces `} else {` with `} else if tt.args.method == "voteWeighted" {`.

## Project Context

The changed code sits primarily in `precompiles/gov`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `precompiles/gov/legacy/v606/gov.go`, `precompiles/gov/legacy/v605/gov.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `precompiles/gov/legacy/v606/gov.go`, `precompiles/gov/legacy/v605/gov.go`. The strongest project-level identifiers around this patch are `method`, `args`, `govtypes`, and `proposalID`.

## Before/After Behavior

Before the patch, vote decoded proposalID and voteOption from ABI arguments and called govKeeper.AddVote directly. After the patch, it builds MsgVote, runs ValidateBasic, wraps the SDK context, and calls govMsgServer.Vote. Before the patch, deposit performed payment handling and called govKeeper.AddDeposit directly. After the patch, it builds MsgDeposit, runs ValidateBasic, wraps the SDK context, and calls govMsgServer.Deposit. The patch also adds handling around VoteWeighted and SubmitProposal gas/ABI/test coverage.

# Root Cause

The supported root cause is architectural inconsistency: some EVM gov precompile transaction paths used direct keeper calls rather than the standard Msg/MsgServer path. The evidence does not prove that this direct path actually bypassed a security-critical check or allowed an invalid state transition.

## Walkthrough

1. An EVM caller reaches the gov precompile vote or deposit entrypoint.

2. The old vote path decoded ABI arguments and called govKeeper.AddVote directly.

3. The patched vote path constructs MsgVote, calls ValidateBasic, and dispatches through govMsgServer.Vote.

4. The old deposit path handled payment and called govKeeper.AddDeposit directly.

5. The patched deposit path constructs MsgDeposit, calls ValidateBasic, and dispatches through govMsgServer.Deposit.

6. Additional changes add or adjust governance precompile methods, gas handling, ABI behavior, and tests.

7. The evidence supports validation-path alignment, but not a demonstrated vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| precompiles/gov/gov.go | 116 | EVM gov precompile vote entrypoint; now builds MsgVote, validates it, and dispatches through gov MsgServer instead of direct keeper AddVote. |
| precompiles/gov/gov.go | 200 | EVM gov precompile deposit entrypoint; now builds MsgDeposit, validates it, and dispatches through gov MsgServer after payment handling. |
| precompiles/gov/gov.go | 50 | Gov precompile registration and gas schedule; adds VoteWeighted and SubmitProposal method handling to the precompile surface. |
| precompiles/gov/gov_test.go | 225 | Tests for updated precompile ABI handling, including weighted vote option payloads and option-count behavior. |

## Code Snippets

## Snippet 1

Context: `precompiles/gov/gov.go:128` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
proposalID := args[0].(uint64)
	voteOption := args[1].(int32)
	err := p.govKeeper.AddVote(ctx, proposalID, voter, govtypes.NewNonSplitVoteOption(govtypes.VoteOption(voteOption)))
	if err != nil {
		return nil, err
```
After
```go
proposalID := args[0].(uint64)
	voteOption := args[1].(int32)

	msg := govtypes.NewMsgVote(voter, proposalID, govtypes.VoteOption(voteOption))
	err := msg.ValidateBasic()
	if err != nil {
		return nil, err
	}
```

## Snippet 2

Context: `precompiles/gov/gov.go:214` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return nil, err
	}
	res, err := p.govKeeper.AddDeposit(ctx, proposalID, depositor, sdk.NewCoins(coin))
	if err != nil {
		return nil, err
	}
	return method.Outputs.Pack(res)
}
```
After
```go
return nil, err
	}

	msg := govtypes.NewMsgDeposit(depositor, proposalID, sdk.NewCoins(coin))
	err = msg.ValidateBasic()
	if err != nil {
		return nil, err
	}
```

## Snippet 3

Context: `precompiles/gov/gov.go:81` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// RequiredGas returns the required bare minimum gas to execute the precompile.
func (p PrecompileExecutor) RequiredGas(input []byte, method *abi.Method) uint64 {
	if bytes.Equal(method.ID, p.VoteID) {
		return 30000
	} else if bytes.Equal(method.ID, p.DepositID) {
		return 30000
	}
```
After
```go
// RequiredGas returns the required bare minimum gas to execute the precompile.
func (p PrecompileExecutor) RequiredGas(input []byte, method *abi.Method) uint64 {
	if bytes.Equal(method.ID, p.VoteID) || bytes.Equal(method.ID, p.VoteWeightedID) {
		return 30000
	} else if bytes.Equal(method.ID, p.DepositID) {
		return 30000
	} else if bytes.Equal(method.ID, p.SubmitProposalID) {
		return 50000
```

## Snippet 4

Context: `precompiles/gov/gov_test.go:231` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
if tt.args.method == "deposit" {
				args, err = abi.Pack(tt.args.method, tt.args.proposal)
			} else {
				args, err = abi.Pack(tt.args.method, tt.args.proposal, tt.args.option)
```
After
```go
if tt.args.method == "deposit" {
				args, err = abi.Pack(tt.args.method, tt.args.proposal)
			} else if tt.args.method == "voteWeighted" {
				// Create weighted vote options for testing
				// Example: 70% Yes, 30% Abstain
				weightedOptions := []struct {
					Option int32  `json:"option"`
					Weight string `json:"weight"`
```

# Fix Pattern

Align EVM precompile transaction execution with the canonical Cosmos SDK governance message path by constructing Msg objects, validating them, and using MsgServer dispatch instead of direct keeper mutation.

## How It Was Fixed

The vote and deposit handlers now create MsgVote and MsgDeposit, call ValidateBasic, wrap the SDK context, and invoke the corresponding gov MsgServer methods. The precompile surface and tests were also updated for additional governance methods such as VoteWeighted and SubmitProposal.

# Why It Matters

1. Keeps EVM precompile behavior closer to native governance transaction behavior.

2. Reduces risk of divergence between direct keeper calls and message-level validation.

3. Makes validation explicit at the ABI-facing boundary.

4. Does not, by itself, prove a security vulnerability was fixed.

# Evidence Notes

Grounded evidence comes from precompiles/gov/gov.go vote and deposit snippets showing replacement of govKeeper.AddVote/AddDeposit with MsgVote/MsgDeposit, ValidateBasic, and govMsgServer calls. The commit notes mention adding msg validation and moving tx methods to MsgServer to leverage msg checks. However, no supplied snippet identifies which check was previously bypassed, whether keeper methods lacked equivalent validation, or whether an attacker could exploit the difference. Heuristic claims about cryptographic, replay-sensitive, consensus, or validator logic are unsupported by the shown code. Protocol security invariant: If treated as security relevant, governance actions submitted through the EVM precompile should follow the same validation and execution semantics as native Cosmos SDK governance messages. The provided evidence shows movement toward that invariant, but does not prove the old path violated it in an exploitable way. Verification notes: The patch does not prove that direct govKeeper.AddVote or AddDeposit allowed an invalid state transition by itself. The patch does not show a demonstrated exploit, fund loss, governance takeover, or consensus failure. The evidence does not establish cryptographic or replay-sensitive logic changes despite heuristic labels. The commit includes broad feature additions and ABI/test updates, so not every changed path is security-relevant. Weighted vote option limiting is indicated by commit/test context, but the provided implementation excerpt is incomplete. No exploit or failing security test is provided. No specific invalid vote, deposit, or weighted-vote payload is shown to have succeeded before the patch. Legacy context excerpts only show imports and do not establish prior vulnerable behavior. Broad feature-addition and ABI/test changes make a pure vulnerability-fix classification unsupported. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validation-bypass-hardening`
Final impact type: `governance-validation-divergence`
Final confidence: `medium`
Final tags: `blockchain-core, evm-precompile, governance, message-validation, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The governance EVM precompile is an exposed transaction path, and the patch changes vote and deposit execution from direct keeper mutation to canonical Msg construction, ValidateBasic checks, and MsgServer dispatch. That clearly tightens validation behavior in a security-sensitive governance path, but the evidence does not prove a concrete exploitable bug, invalid payload accepted before, fund loss, governance takeover, or consensus failure.

## Security Evidence

1. Vote now constructs MsgVote, calls ValidateBasic, and dispatches through govMsgServer.Vote instead of directly calling govKeeper.AddVote.
2. Deposit now constructs MsgDeposit, calls ValidateBasic, and dispatches through govMsgServer.Deposit instead of directly calling govKeeper.AddDeposit.
3. Commit notes explicitly mention adding message validation and moving gov precompile tx methods to MsgServer to leverage message checks.
4. The changed path is an EVM-facing governance precompile, which is security-sensitive because it can affect proposal voting and deposits.

## Missing Evidence

1. No supplied evidence shows which specific ValidateBasic or MsgServer check was previously bypassed.
2. No exploit scenario or failing security test demonstrates that an invalid vote, deposit, or weighted vote succeeded before the patch.
3. No evidence establishes fund loss, governance takeover, privilege escalation, replay, cryptographic failure, or consensus divergence.
4. The commit also includes broad feature work for missing governance precompile methods, ABI updates, gas handling, and tests.

## Claim Boundaries

1. Classify as security-hardening only, not security-fix.
2. Do not claim a proven vulnerability or concrete exploit from the supplied evidence.
3. Do not retain the original serialization-or-state-representation bug class; the supported issue is validation-path hardening.
4. Do not rely on heuristic labels about cryptographic, replay-sensitive, validator, or consensus logic because the snippets do not support those claims.
