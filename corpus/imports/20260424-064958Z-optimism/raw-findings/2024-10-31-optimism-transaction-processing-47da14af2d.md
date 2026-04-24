---
case_id: case_20241031_47da14af2d
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-10-31
source_refs:
  - git:47da14af2d4fc75fcf9cac9d8dbb38f64d1b8e46
  - "op-node/rollup/derive/attributes_queue.go:137"
  - "op-node/rollup/engine/payload_process.go:31"
  - "op-node/rollup/derive/deriver.go:145"
  - "op-service/eth/types.go:359"
bug_class: invalid-payload-handling
impact_type:
  - availability
confidence: medium
tags:
  - blockchain-core
  - consensus
  - rollup
  - invalid-payload
  - state-reset
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a protocol-correctness change for Holocene invalid payload handling, not a clearly established vulnerability fix. The patch adds a Holocene-specific deposits-only fallback path, wires that path into the derivation pipeline, and clears cached attribute state on reset, but the provided diff does not prove exploitability or a concrete security failure.

## Observed Patch Facts

1. In `op-node/rollup/derive/attributes_queue.go`, the patch replaces `func (aq *AttributesQueue) Reset(ctx context.Context, _ eth.L1BlockRef, _ eth.SystemC...` with `func (aq *AttributesQueue) reset() {`.

2. In `op-node/rollup/engine/payload_process.go`, the patch replaces `Err: fmt.Errorf("failed to insert execution payload: %w", err)})` with `Err: fmt.Errorf("failed to insert execution payload: %w", err),`.

3. In `op-node/rollup/derive/deriver.go`, the patch replaces `default:` with `case DepositsOnlyPayloadAttributesRequestEvent:`.

4. In `op-service/eth/types.go`, the patch replaces `type ExecutePayloadStatus string` with `// IsDepositsOnly returns whether all transactions of the PayloadAttributes are of De...`.

## Project Context

The changed code sits primarily in `op-node/rollup/derive`, `op-node/rollup`, `op-node/rollup/engine`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-node/rollup/derive/span_batch_tx.go`, `op-node/rollup/derive/span_batch.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-node/rollup/derive/span_batch_tx.go`, `op-node/rollup/derive/span_batch.go`. The strongest project-level identifiers around this patch are `Errorf`, `transactions`, `AttributesQueue`, and `batch`. Nearby tests or test-like files include `op-node/rollup/derive/fuzz_parsers_test.go`, `op-node/rollup/derive/test/random.go`.

## Before/After Behavior

Before the patch, the shown invalid-payload path in `op-node/rollup/engine/payload_process.go` did not include the Holocene deposits-only fallback, `PipelineDeriver.OnEvent` had no handler for a deposits-only attributes request, and `AttributesQueue.Reset(...)` did not clear `lastAttribs`. After the patch, Holocene invalid payloads can trigger a deposits-only re-derivation flow, the deriver handles that request, and reset logic clears cached `lastAttribs`; helper logic was also added to classify deposit-only payload attributes.

# Root Cause

The shown pre-patch logic lacked an explicit Holocene recovery path for execution-invalid payload attributes and did not clear all relevant cached attribute state on reset. The evidence supports a correctness/state-management gap, but not a proven security vulnerability.

## Walkthrough

1. `op-node/rollup/engine/payload_process.go` now checks for invalid execution status and, for non-zero `DerivedFrom` values during Holocene, emits a deposits-only payload-attributes request instead of immediately staying on the ordinary invalid-payload path.

2. `op-node/rollup/derive/deriver.go` adds `DepositsOnlyPayloadAttributesRequestEvent` handling and calls `pipeline.DepositsOnlyAttributes(x.Parent, x.DerivedFrom)` to produce replacement attributes.

3. `op-node/rollup/derive/attributes_queue.go` refactors reset logic into `reset()` and newly clears `aq.lastAttribs = nil`, showing cached attribute state is now explicitly reset.

4. The same attributes queue code still shows normal attribute creation appending full `batch.Transactions`, so the new path is a narrower alternative rather than the default behavior.

5. `op-service/eth/types.go` adds `PayloadAttributes.IsDepositsOnly()` to classify whether all transactions are deposit transactions, supporting the new deposits-only handling path.

6. These changes collectively show protocol-specific fallback and state cleanup, but the provided evidence does not establish attacker control, exploitability, or a concrete pre-patch security break.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-node/rollup/engine/payload_process.go | 25 | detects invalid execution payloads and, for Holocene-derived blocks, requests deposits-only fallback attributes instead of treating the payload path as terminally invalid |
| op-node/rollup/derive/deriver.go | 101 | handles the new deposits-only attributes request event and re-derives payload attributes from the derivation pipeline |
| op-node/rollup/derive/attributes_queue.go | 113 | builds deterministic payload attributes from batches and resets cached attribute state so invalid attributes are not retained across retries |
| op-service/eth/types.go | 337 | adds helpers to recognize deposit-only payload attributes, supporting the fallback path's transaction filtering semantics |

## Code Snippets

## Snippet 1

Context: `op-node/rollup/derive/attributes_queue.go:137` (changes signature or replay validation logic)

Before
```go
}

func (aq *AttributesQueue) Reset(ctx context.Context, _ eth.L1BlockRef, _ eth.SystemConfig) error {
	aq.batch = nil
	aq.isLastInSpan = false // overwritten later, but set for consistency
	return io.EOF
}
```
After
```go
}

func (aq *AttributesQueue) reset() {
	aq.batch = nil
	aq.isLastInSpan = false // overwritten later, but set for consistency
	aq.lastAttribs = nil
}
```

## Snippet 2

Context: `op-node/rollup/engine/payload_process.go:31` (changes a sensitive control or state-update path)

Before
```go
if err != nil {
		eq.emitter.Emit(rollup.EngineTemporaryErrorEvent{
			Err: fmt.Errorf("failed to insert execution payload: %w", err)})
		return
	}
	switch status.Status {
	case eth.ExecutionInvalid, eth.ExecutionInvalidBlockHash:
		eq.emitter.Emit(PayloadInvalidEvent{
```
After
```go
if err != nil {
		eq.emitter.Emit(rollup.EngineTemporaryErrorEvent{
			Err: fmt.Errorf("failed to insert execution payload: %w", err),
		})
		return
	}
	switch status.Status {
	case eth.ExecutionInvalid, eth.ExecutionInvalidBlockHash:
```

## Snippet 3

Context: `op-node/rollup/derive/deriver.go:145` (changes a sensitive control or state-update path)

Before
```go
case ConfirmReceivedAttributesEvent:
		d.needAttributesConfirmation = false
	default:
		return false
```
After
```go
case ConfirmReceivedAttributesEvent:
		d.needAttributesConfirmation = false
	case DepositsOnlyPayloadAttributesRequestEvent:
		d.pipeline.log.Warn("Deriving deposits-only attributes", "origin", d.pipeline.Origin())
		attrib, err := d.pipeline.DepositsOnlyAttributes(x.Parent, x.DerivedFrom)
		if err != nil {
			d.emitter.Emit(rollup.CriticalErrorEvent{Err: fmt.Errorf("deriving deposits-only attributes: %w", err)})
			return true
```

## Snippet 4

Context: `op-service/eth/types.go:359` (changes a sensitive control or state-update path)

Before
```go
}

type ExecutePayloadStatus string
```
After
```go
}

// IsDepositsOnly returns whether all transactions of the PayloadAttributes are of Deposit
// type. Empty transactions are also considered non-Deposit transactions.
func (a *PayloadAttributes) IsDepositsOnly() bool {
	for _, tx := range a.Transactions {
		if len(tx) == 0 || tx[0] != types.DepositTxType {
			return false
```

# Fix Pattern

Add a protocol-specific fallback path for invalid derived payloads and clear cached derivation state so retries or recovery do not reuse stale attributes.

## How It Was Fixed

When execution marks a Holocene-derived payload invalid, the node now requests deposits-only attributes derived from the parent block and L1 origin. The derivation pipeline handles that request and emits re-derived attributes, while reset handling now clears `lastAttribs` so stale cached attributes do not persist across recovery/reset flows. A helper was also added to recognize deposit-only payload attributes.

# Why It Matters

1. Improves deterministic handling of invalid payload attributes during a protocol-upgrade-specific path.

2. Reduces the chance that stale cached attributes remain after reset.

3. Makes deposits-only fallback behavior explicit in the derivation pipeline.

4. Does not show silent acceptance of invalid payloads.

# Evidence Notes

The strongest evidence is in `op-node/rollup/engine/payload_process.go`, `op-node/rollup/derive/deriver.go`, `op-node/rollup/derive/attributes_queue.go`, and `op-service/eth/types.go`. Those hunks show fallback routing, new event handling, cache clearing, and deposit-only classification. The provided material does not show a concrete exploit path, externally triggerable attacker model, or direct evidence that the pre-patch behavior was exploitable as a security issue. Protocol security invariant: For Holocene-derived blocks, nodes should handle execution-invalid sequencer attributes deterministically: avoid reusing stale cached attributes and, when appropriate, re-derive a deposits-only payload from L1-derived context so node behavior stays consistent. Verification notes: The patch does not prove an externally reachable exploit or attacker-controlled trigger beyond invalid sequencer-derived payload content. It does not show silent acceptance of invalid payloads; the visible behavior is fallback to deposits-only derivation. It does not establish resource exhaustion as the primary bug shape. It does not prove pre-patch chain takeover; the evidence supports consensus-safety and availability hardening around Holocene invalid payload handling. Tests were added or updated, but their detailed assertions are not included in the provided evidence. The diff supports a Holocene invalid-payload recovery change more clearly than a confirmed vulnerability fix. Security relevance is plausible because the code is in consensus/derivation logic, but the vulnerability thesis is not established by the provided hunks alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invalid-payload-handling`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, rollup, invalid-payload, state-reset, hardening`

The patch is in consensus/derivation code and clearly tightens handling of invalid Holocene payloads by switching to a deposits-only recovery path and clearing cached attributes on reset. That supports a security-hardening interpretation around consensus-safety and liveness under malformed or invalid sequencer input. However, the provided hunks do not prove a concrete exploitable vulnerability, so this should not be treated as a confirmed security-fix, and the original resource-exhaustion/remote-dos labeling is too specific.

## Security Evidence

1. `payload_process.go` adds Holocene-specific handling for `ExecutionInvalid` / `ExecutionInvalidBlockHash` and requests deposits-only attributes instead of following the ordinary invalid path.
2. `deriver.go` wires a new `DepositsOnlyPayloadAttributesRequestEvent` into the derivation pipeline, showing an explicit recovery path for invalid payload attributes.
3. `attributes_queue.go` now clears `lastAttribs` during reset, reducing the risk of stale derived state being reused after invalid payload handling.
4. `types.go` adds `IsDepositsOnly()`, indicating the fallback path intentionally constrains payload contents to deposit transactions only.
5. The touched files and tests are in rollup/engine/derivation and include `bad_tx_in_batch_test.go` and `holocene_fork_test.go`, which is consistent with hardening malformed/invalid batch handling in consensus-sensitive code.

## Missing Evidence

1. No advisory, bug report, or commit text states that a security vulnerability existed before the patch.
2. The diff does not show attacker control, exploit steps, or a demonstrated chain split / remote DoS scenario.
3. The provided test evidence does not include assertions proving a concrete pre-patch security failure.
4. Nothing in the shown patch supports the original `resource-exhaustion` classification.

## Claim Boundaries

1. Supported claim: this is security-relevant hardening of invalid payload handling in consensus-sensitive rollup logic.
2. Supported claim: the patch improves deterministic recovery/state cleanup when Holocene-derived payloads are invalid.
3. Not supported: a confirmed exploitable vulnerability fix.
4. Not supported: `resource-exhaustion` or `remote-dos` as the demonstrated bug class/impact from the patch alone.
