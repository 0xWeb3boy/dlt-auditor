---
case_id: case_20210215_a0ac508da
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: medium
date: 2021-02-15
source_refs:
  - git:a0ac508dafff15a93bf9f2a6732884a984a62fab
  - "go/consensus/tendermint/apps/roothash/transactions_test.go:476"
  - "go/oasis-node/cmd/debug/byzantine/byzantine.go:227"
  - "go/roothash/api/commitment/executor.go:313"
  - "go/roothash/api/commitment/executor.go:108"
bug_class: insufficient-signature-domain-separation
impact_type:
  - integrity
tags:
  - cryptography
  - consensus
  - signature
  - domain-separation
  - runtime-binding
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes executor-commitment and proposed-batch signature verification to derive runtime-specific signature contexts, and updates evidence handling to treat runtime-mismatched signed data as invalid evidence. That is direct evidence of a protocol authentication/domain-separation fix in a consensus-sensitive path.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/roothash/transactions_test.go`, the patch replaces `roothash.ErrInvalidRuntime,` with `roothash.ErrInvalidEvidence,`.

2. In `go/oasis-node/cmd/debug/byzantine/byzantine.go`, the patch replaces `if err = cbc.createCommitment(b.identity, b.rak, b.executorCommittee.EncodedMembersHa...` with `if err = cbc.createCommitment(b.identity, defaultRuntimeID, b.rak, b.executorCommitte...`.

3. In `go/roothash/api/commitment/executor.go`, the patch replaces `func (c *ExecutorCommitment) Open() (*OpenExecutorCommitment, error) {` with `func (c *ExecutorCommitment) Open(runtimeID common.Namespace) (*OpenExecutorCommitmen...`.

4. In `go/roothash/api/commitment/executor.go`, the patch replaces `func (m *ComputeBody) VerifyTxnSchedSignature(header block.Header) bool {` with `func (m *ComputeBody) VerifyTxnSchedSignature(runtimeID common.Namespace, header bloc...`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/roothash`, `go/consensus/tendermint/apps`, `go/oasis-node/cmd/debug/byzantine`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/oasis-node/cmd/debug/byzantine/executor.go`, `go/roothash/api/commitment/txnscheduler.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/oasis-node/cmd/debug/byzantine/executor.go`, `go/roothash/api/commitment/txnscheduler.go`. The strongest project-level identifiers around this patch are `commitment`, `signature`, `error`, and `Open`.

## Before/After Behavior

Before the change, the shown verification paths used shared signature contexts and did not take a runtime ID as part of signature-context derivation. After the change, both `ExecutorCommitment.Open` and `ComputeBody.VerifyTxnSchedSignature` require `runtimeID` and derive runtime-suffixed contexts with `WithSuffix(runtimeID.String())`; helper code that creates commitments is updated to pass an explicit runtime ID, and a test now expects a runtime mismatch to fail as `ErrInvalidEvidence`.

# Root Cause

Runtime ID was not incorporated into the signature context for the shown roothash commitment-verification paths, so the signature domain was not explicitly separated per runtime.

## Walkthrough

1. `go/roothash/api/commitment/executor.go` changes `ExecutorCommitment.Open()` to `Open(runtimeID common.Namespace)` and derives `ExecutorSignatureContext.WithSuffix(runtimeID.String())` before signature verification.

2. The same file changes `ComputeBody.VerifyTxnSchedSignature` to take `runtimeID` and derive `ProposedBatchSignatureContext.WithSuffix(runtimeID.String())` before verifying the rebuilt batch.

3. `go/oasis-node/cmd/debug/byzantine/byzantine.go` is updated so commitment creation passes `defaultRuntimeID`, showing signing helpers now need an explicit runtime.

4. `go/consensus/tendermint/apps/roothash/transactions_test.go` changes the expected result for a signed-batch/runtime mismatch from `ErrInvalidRuntime` to `ErrInvalidEvidence` with a runtime-mismatch-specific message.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/roothash/api/commitment/executor.go | 309 | executor commitment signature verification now includes runtime-specific domain separation |
| go/roothash/api/commitment/executor.go | 97 | transaction scheduler batch signature verification now includes runtime-specific domain separation |
| go/consensus/tendermint/apps/roothash/transactions_test.go | 476 | consensus evidence validation regression coverage for runtime-mismatched signed batches |
| go/oasis-node/cmd/debug/byzantine/byzantine.go | 227 | test/byzantine commitment generation updated to sign for an explicit runtime |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/roothash/transactions_test.go:476` (changes a sensitive control or state-update path)

Before
```go
},
			},
			roothash.ErrInvalidRuntime,
			"evidence for nonexisting runtime",
		},
		{
```
After
```go
},
			},
			roothash.ErrInvalidEvidence,
			"invalid evidence (signed batch runtime does not match evidence runtime)",
		},
		{
```

## Snippet 2

Context: `go/oasis-node/cmd/debug/byzantine/byzantine.go:227` (changes a sensitive control or state-update path)

Before
```go
switch executorMode {
	case ModeExecutorFailureIndicating:
		if err = cbc.createCommitment(b.identity, b.rak, b.executorCommittee.EncodedMembersHash(), commitment.FailureUnknown); err != nil {
			panic(fmt.Sprintf("compute create commitment failed: %+v", err))
		}
	default:
		if err = cbc.createCommitment(b.identity, b.rak, b.executorCommittee.EncodedMembersHash(), commitment.FailureNone); err != nil {
			panic(fmt.Sprintf("compute create commitment failed: %+v", err))
```
After
```go
switch executorMode {
	case ModeExecutorFailureIndicating:
		if err = cbc.createCommitment(b.identity, defaultRuntimeID, b.rak, b.executorCommittee.EncodedMembersHash(), commitment.FailureUnknown); err != nil {
			panic(fmt.Sprintf("compute create commitment failed: %+v", err))
		}
	default:
		if err = cbc.createCommitment(b.identity, defaultRuntimeID, b.rak, b.executorCommittee.EncodedMembersHash(), commitment.FailureNone); err != nil {
			panic(fmt.Sprintf("compute create commitment failed: %+v", err))
```

## Snippet 3

Context: `go/roothash/api/commitment/executor.go:313` (changes signature or replay validation logic)

Before
```go
// Open validates the executor commitment signature, and de-serializes the message.
// This does not validate the RAK signature.
func (c *ExecutorCommitment) Open() (*OpenExecutorCommitment, error) {
	var body ComputeBody
	if err := c.Signed.Open(ExecutorSignatureContext, &body); err != nil {
		return nil, errors.New("roothash/commitment: commitment has invalid signature")
	}
```
After
```go
// Open validates the executor commitment signature, and de-serializes the message.
// This does not validate the RAK signature.
func (c *ExecutorCommitment) Open(runtimeID common.Namespace) (*OpenExecutorCommitment, error) {
	sigCtx, err := ExecutorSignatureContext.WithSuffix(runtimeID.String())
	if err != nil {
		return nil, fmt.Errorf("roothash/commitment: signature context error: %w", err)
	}
```

## Snippet 4

Context: `go/roothash/api/commitment/executor.go:108` (changes signature or replay validation logic)

Before
```go
// in the ComputeBody struct and verifies if the txn scheduler signature
// matches what we're seeing.
func (m *ComputeBody) VerifyTxnSchedSignature(header block.Header) bool {
	dispatch := &ProposedBatch{
		IORoot:            m.InputRoot,
```
After
```go
// in the ComputeBody struct and verifies if the txn scheduler signature
// matches what we're seeing.
func (m *ComputeBody) VerifyTxnSchedSignature(runtimeID common.Namespace, header block.Header) (bool, error) {
	ctx, err := ProposedBatchSignatureContext.WithSuffix(runtimeID.String())
	if err != nil {
		return false, fmt.Errorf("proposed batch signature context error: %w", err)
	}
	dispatch := &ProposedBatch{
```

# Fix Pattern

Bind protocol signatures to the full security domain they are meant to authenticate by adding the missing domain identifier to signature-context derivation and propagating that identifier through signing and verification.

## How It Was Fixed

The fix threads `runtimeID` into the affected verification paths, derives runtime-qualified signature contexts via `WithSuffix(runtimeID.String())`, updates commitment-generation helpers to sign with an explicit runtime, and adds regression coverage for runtime-mismatched evidence.

# Why It Matters

1. Runtime identity becomes part of the authenticated signature domain.

2. Consensus-sensitive signed data is less likely to be accepted outside its intended runtime context.

3. The updated test documents that runtime-mismatched signed data is treated as invalid evidence, not a generic runtime lookup issue.

# Evidence Notes

The strongest support is the direct code change from global contexts to runtime-suffixed contexts in `go/roothash/api/commitment/executor.go`, plus the updated runtime-mismatch test and the helper change that now passes a runtime ID at commitment creation. The evidence supports a signature domain-separation flaw and its fix. It does not by itself establish a broader exploit narrative beyond incorrect cross-runtime authentication semantics. Protocol security invariant: Executor commitments and proposed-batch scheduler signatures must be bound to the specific runtime they belong to. A signature that verifies in one runtime context must not verify in another runtime context. Verification notes: The patch shows a signature-domain separation fix, but does not by itself prove a publicly exploitable cross-runtime attack path. The evidence does not show key compromise, signature forgery, or arbitrary code execution. Impact beyond acceptance/rejection of malformed or replayed cross-runtime commitments is not demonstrated by the patch alone. The byzantine tooling change is supporting context, not proof of production exploitability. The provided snippets directly show `runtimeID` added to both relevant verification APIs. The snippets directly show `WithSuffix(runtimeID.String())` replacing plain shared-context verification. The regression test directly shows runtime-mismatched signed evidence is now rejected as invalid evidence. Impact beyond this authentication invariant is not demonstrated by the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-signature-domain-separation`
Final impact type: `integrity`
Final tags: `cryptography, consensus, signature, domain-separation, runtime-binding`

The patch is clearly security-relevant, but the supplied evidence supports it more as security hardening than as a proven exploitable vulnerability fix. The code changes bind executor-commitment and proposed-batch signature verification to a specific runtime by deriving runtime-suffixed signature contexts, and the updated test shows runtime-mismatched signed evidence is now rejected as invalid evidence. That is strong evidence of tightened authentication/domain-separation semantics in a consensus-sensitive path, while the record does not prove a concrete pre-patch exploit or the original liveness-focused bug class.

## Security Evidence

1. Executor commitment verification now requires `runtimeID` and uses `ExecutorSignatureContext.WithSuffix(runtimeID.String())`.
2. Transaction scheduler signature verification now requires `runtimeID` and uses `ProposedBatchSignatureContext.WithSuffix(runtimeID.String())`.
3. Supporting signing/helper code was updated to pass an explicit runtime ID when creating commitments.
4. Regression coverage now expects a signed-batch/runtime mismatch to be rejected as `ErrInvalidEvidence` with a runtime-mismatch-specific message.

## Missing Evidence

1. No direct proof that cross-runtime signed data was accepted in production before the patch.
2. No exploit narrative or reproducer shows attacker-triggerable replay, forgery, or consensus break.
3. The patch does not demonstrate the originally claimed `liveness-failure` impact.

## Claim Boundaries

1. The evidence supports a signature-domain-separation hardening entry, not a proven end-to-end exploit.
2. The patch shows stronger runtime binding for signatures; it does not show key compromise or signature forgery.
3. The safe claim is reduced risk of accepting mismatched cross-runtime signed data, not broader liveness or RCE impact.
