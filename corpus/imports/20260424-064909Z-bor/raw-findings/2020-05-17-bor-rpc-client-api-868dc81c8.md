---
case_id: case_20200517_868dc81c8
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2020-05-17
source_refs:
  - git:868dc81c8ae37dd8dd06dbb7335f00cdc6d75ecc
  - "consensus/bor/bor.go:868"
  - "consensus/bor/bor.go:1181"
  - "consensus/bor/bor.go:1116"
  - "consensus/bor/bor.go:704"
bug_class: fail-open-error-handling
impact_type:
  - state-consistency
confidence: medium
tags:
  - consensus
  - state-sync
  - error-handling
  - fail-closed
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Bor's sprint-boundary state-sync flow to return an error when `CommitStates` fails, adds an early `c.config.Sprint` guard, moves state commit work into `genesisContractsClient`, and replaces a local span-pending helper with a current-span contract read. That is evidence of consensus/state-transition refactoring or hardening, but the provided excerpts do not establish a concrete vulnerability or show that the prior behavior was exploitable.

## Observed Patch Facts

1. In `consensus/bor/bor.go`, the patch replaces `// Checks if "force" proposeSpan has been set` with `// GetCurrentSpan get current span from contract`.

2. In `consensus/bor/bor.go`, the patch replaces `recordBytes, err := rlp.EncodeToBytes(eventRecord)` with `if err := c.genesisContractsClient.CommitState(eventRecord, state, header, chain); er...`.

3. In `consensus/bor/bor.go`, the patch replaces `chain core.ChainContext,` with `chain chainContext,`.

4. In `consensus/bor/bor.go`, the patch replaces `// return nil, err` with `return nil, err`.

## Project Context

The changed code sits primarily in `consensus/bor`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `consensus/bor/errors.go`, `consensus/bor/genesis_contracts_client.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/bor/genesis_contracts_client.go`, `consensus/bor/validator.go`. The strongest project-level identifiers around this patch are `state`, `error`, `header`, and `Error`. Nearby tests or test-like files include `consensus/bor/bor_test/bor_test.go`, `consensus/bor/bor_test/states.json`.

## Before/After Behavior

Before the change, `FinalizeAndAssemble` logged `CommitStates` errors and continued because the return was commented out. `CommitStates` also performed local record encoding/ABI packing in `bor.go`. After the change, finalization returns the error, `CommitStates` rejects calls before the sprint threshold, state commits are delegated to `genesisContractsClient.CommitState(...)`, and the nearby span helper is replaced by `GetCurrentSpan(...)` using a contract call.

# Root Cause

The only clearly supported issue is permissive error handling in a consensus-related path: `FinalizeAndAssemble` could continue after `CommitStates` failed. The rest of the diff shows restructuring around canonical contract-backed helpers, but the evidence does not prove the old local logic was unsafe rather than simply being replaced.

## Walkthrough

1. `FinalizeAndAssemble` changed from logging `CommitStates` failure and continuing to returning the error immediately.

2. `CommitStates` now checks `header.Number.Uint64()` against `c.config.Sprint` and errors out when called too early.

3. The state commit path in `bor.go` no longer locally RLP-encodes and ABI-packs `commitState`; it now calls `c.genesisContractsClient.CommitState(...)`.

4. A nearby helper named `isSpanPending` was removed and replaced with `GetCurrentSpan`, which calls the validator-set contract for the current span.

5. These changes are all in Bor consensus/state-sync code, but the excerpts do not show a demonstrated exploit path or concrete desynchronization outcome.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/bor/bor.go | 691 | block finalization path now fails closed if state-sync commit fails |
| consensus/bor/bor.go | 1115 | state-sync commit scheduling and precondition checks at sprint boundaries |
| consensus/bor/bor.go | 1175 | state-sync event commit path delegated to genesis-contract client |
| consensus/bor/bor.go | 866 | current span retrieval from validator-set contract for consensus/span selection |

## Code Snippets

## Snippet 1

Context: `consensus/bor/bor.go:868` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// Checks if "force" proposeSpan has been set
func (c *Bor) isSpanPending(snapshotNumber uint64) (bool, error) {
	blockNr := rpc.BlockNumber(snapshotNumber)
	method := "spanProposalPending"

	// get packed data
```
After
```go
}

// GetCurrentSpan get current span from contract
func (c *Bor) GetCurrentSpan(snapshotNumber uint64) (*Span, error) {
```

## Snippet 2

Context: `consensus/bor/bor.go:1181` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
TxHash:   eventRecord.TxHash,
		}

		go func() {
			c.stateDataFeed.Send(core.NewStateChangeEvent{StateData: &stateData})
		}()

		recordBytes, err := rlp.EncodeToBytes(eventRecord)
```
After
```go
TxHash:   eventRecord.TxHash,
		}
		go func() {
			c.stateDataFeed.Send(core.NewStateChangeEvent{StateData: &stateData})
		}()

		if err := c.genesisContractsClient.CommitState(eventRecord, state, header, chain); err != nil {
			return err
```

## Snippet 3

Context: `consensus/bor/bor.go:1116` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
state *state.StateDB,
	header *types.Header,
	chain core.ChainContext,
) error {
	// get pending state proposals
	stateIds, err := c.GetPendingStateProposals(header.Number.Uint64() - 1)
	if err != nil {
		return err
```
After
```go
state *state.StateDB,
	header *types.Header,
	chain chainContext,
) error {
	number := header.Number.Uint64()
	if number < c.config.Sprint {
		return errors.New("Requested to commit states too soon")
	}
```

## Snippet 4

Context: `consensus/bor/bor.go:704` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
if err := c.CommitStates(state, header, cx); err != nil {
			log.Error("Error while committing states", "error", err)
			// return nil, err
		}
	}
```
After
```go
if err := c.CommitStates(state, header, cx); err != nil {
			log.Error("Error while committing states", "error", err)
			return nil, err
		}
	}
```

# Fix Pattern

Fail closed on consensus-path errors and centralize state-sync/span interactions behind explicit contract-backed helper calls.

## How It Was Fixed

The patch restored error propagation in `FinalizeAndAssemble`, added a sprint-threshold precondition inside `CommitStates`, delegated state commit logic to `genesisContractsClient`, and switched the changed span-related helper to a contract-backed current-span fetch.

# Why It Matters

1. Continuing block assembly after a failed state-sync commit is a risky pattern in consensus code.

2. Centralizing contract interactions can reduce divergence between duplicated local call sites.

3. The excerpts still do not prove that the old behavior led to an exploitable security flaw.

# Evidence Notes

Strongest evidence: the commented-out `return nil, err` was reinstated in `FinalizeAndAssemble`, and `CommitStates` was reworked around `genesisContractsClient`. The supplied material does not show the full old and new logic for span/state-sync validation, does not show an exploit scenario, and does not prove chain safety impact. Claims such as unauthorized state injection, validator forgery, or confirmed desync are unsupported by the provided excerpts. Protocol security invariant: If sprint-boundary state-sync or span-dependent consensus work is required for correct block production, validators should use the canonical state source and should not finalize a block after those operations fail. Verification notes: The patch does not prove a remotely exploitable attack path. The patch does not show unauthorized state injection or validator forgery. The patch does not prove a real-world chain split occurred before the change. The patch does not demonstrate a cryptographic break; it shows consensus/state-transition correctness tightening. The patch alone does not establish that the new genesis-contract client enforces all necessary validation. No full diff or surrounding control flow was provided beyond selected excerpts. Security relevance is plausible because the code is in consensus/state-sync paths, but it is not established by the evidence alone. This should be treated as unclear rather than a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fail-open-error-handling`
Final impact type: `state-consistency`
Final confidence: `medium`
Final tags: `consensus, state-sync, error-handling, fail-closed, hardening`

The patch clearly tightens behavior in a consensus-critical state-sync path: block finalization now aborts when `CommitStates` fails, premature state commits are explicitly rejected, and state/span handling is moved toward canonical contract-backed helpers. In blockchain consensus code, that is security-relevant hardening because it removes fail-open behavior around state transition logic. The evidence does not, however, prove a concrete exploitable vulnerability, attacker capability, or demonstrated chain split, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `FinalizeAndAssemble` changed from logging `CommitStates` failure and continuing to returning the error, which is a fail-closed change in consensus logic.
2. `CommitStates` now rejects execution before `c.config.Sprint`, adding an explicit guard on when state-sync commits may occur.
3. State commit logic was centralized behind `genesisContractsClient.CommitState(...)` instead of inline encoding/packing in `bor.go`, reducing ad hoc handling in a sensitive path.
4. The changed code is in `consensus/bor`, directly affecting span/state-sync behavior used during block finalization.

## Missing Evidence

1. No proof that the old behavior was attacker-triggerable from an external interface.
2. No evidence of an actual exploit, chain split, unauthorized state injection, or validator forgery caused by the prior code.
3. No full diff or test evidence here showing the exact invariant that could be violated before the patch.

## Claim Boundaries

1. Supported claim: the commit hardens consensus/state-sync handling by failing closed and adding stricter preconditions.
2. Not supported: a confirmed exploitable vulnerability or real-world security incident before the patch.
3. Not supported: the original `rpc-client-api` or `serialization-or-state-representation` framing as the primary bug class from the shown evidence.
