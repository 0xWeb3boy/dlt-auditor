---
case_id: case_20220426_431274830a
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2022-04-26
source_refs:
  - git:431274830a0c6db6edd0ed417764ef6db6bb80fd
  - "opnode/rollup/driver/step.go:90"
  - "opnode/rollup/driver/step.go:177"
  - "opnode/rollup/derive/payload_attributes.go:344"
  - "opnode/rollup/derive/payload_attributes.go:202"
bug_class: denial-of-service
impact_type:
  - availability
confidence: medium
tags:
  - availability
  - malformed-input
  - error-isolation
  - rollup
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided code evidence supports a security-relevant fix in the opnode deposit derivation path. Before the patch, one malformed deposit log or one deposit encoding failure caused `DeriveDeposits` to return a fatal error, and the driver aborted block or epoch processing for that L1 input. After the patch, derivation collects per-deposit errors, keeps valid deposits, and the driver logs bad entries instead of failing the whole batch. The commit body also claims a contract-side `gasLimit` width reduction to prevent unparsable values, but that specific hunk is not included in the supplied evidence.

## Observed Patch Facts

1. In `opnode/rollup/driver/step.go`, the patch replaces `deposits, err := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)` with `deposits, errs := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)`.

2. In `opnode/rollup/driver/step.go`, the patch replaces `deposits, err := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)` with `deposits, errs := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)`.

3. In `opnode/rollup/derive/payload_attributes.go`, the patch replaces `func DeriveDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([...` with `func DeriveDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([...`.

4. In `opnode/rollup/derive/payload_attributes.go`, the patch replaces `func UserDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]*...` with `func UserDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]*...`.

## Project Context

The changed code sits primarily in `opnode/rollup/driver`, `opnode/rollup`, `opnode/rollup/derive`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `opnode/rollup/derive/payload_attributes_test.go`, `opnode/rollup/driver/driver.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `opnode/rollup/derive/payload_attributes_test.go`, `opnode/rollup/driver/driver.go`. The strongest project-level identifiers around this patch are `receipts`, `deposits`, `errs`, and `derive`.

## Before/After Behavior

Before the patch, `UserDeposits` and `DeriveDeposits` returned a single `error`, so one malformed deposit log or one encoding failure stopped derivation entirely, and both `createNewBlock` and `insertEpoch` returned an error instead of continuing. After the patch, both functions return successful deposits plus `[]error`; malformed or unencodable deposits are skipped, individual errors are logged, and valid deposits still flow into block or epoch processing. Separately, the commit message says deposit `gasLimit` was narrowed from `uint256` to `uint64`, but that change is not directly shown in the provided hunks.

# Root Cause

The direct root cause in the shown code is batch-wide fail-fast handling in the deposit parsing and encoding pipeline: one bad deposit entry was promoted into a fatal error for the entire derivation step. The commit message suggests an additional source of parse failure was a width mismatch around user-supplied `gasLimit`, but the exact contract-side code for that is not part of the supplied evidence.

## Walkthrough

1. `createNewBlock` changed from treating any `DeriveDeposits` error as fatal to iterating over `errs` and continuing.

2. `insertEpoch` made the same control-flow change: deposit derivation errors are logged per item instead of aborting the epoch path.

3. `DeriveDeposits` changed its return type from `([]hexutil.Bytes, error)` to `([]hexutil.Bytes, []error)`.

4. Within `DeriveDeposits`, deposit transaction marshal failures no longer cause immediate return; the code records an error and keeps other encoded deposits.

5. `UserDeposits` likewise changed from returning one `error` to returning `[]error`, and malformed deposit logs are recorded with receipt/log indexes.

6. Because only successfully parsed deposits are appended in `UserDeposits` and only successfully encoded deposits are appended in `DeriveDeposits`, valid deposits continue through the pipeline when one entry is bad.

7. The commit body states there was also an upstream `gasLimit` type reduction to avoid producing values the node cannot parse, but that part is only commit-message evidence here.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| opnode/rollup/driver/step.go | 57 | block construction path now continues after individual deposit derivation errors instead of failing the whole block |
| opnode/rollup/driver/step.go | 148 | epoch insertion path now tolerates and logs per-deposit parsing failures rather than aborting derivation |
| opnode/rollup/derive/payload_attributes.go | 174 | receipt/log scanning changed from single fatal error to collecting malformed deposit errors per receipt/log |
| opnode/rollup/derive/payload_attributes.go | 337 | deposit transaction encoding changed from single fatal error return to partial success with error list |

## Code Snippets

## Snippet 1

Context: `opnode/rollup/driver/step.go:90` (changes a sensitive control or state-update path)

Before
```go
// Next we append user deposits. If we're not the first block in an epoch, then receipts will
	// be empty and no deposits will be derived.
	deposits, err := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)
	d.log.Info("Derived deposits", "deposits", deposits, "l2Parent", l2Head, "l1Origin", l1Origin)
	if err != nil {
		return l2Head, nil, fmt.Errorf("failed to derive deposits: %v", err)
	}
	txns = append(txns, deposits...)
```
After
```go
// Next we append user deposits. If we're not the first block in an epoch, then receipts will
	// be empty and no deposits will be derived.
	deposits, errs := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)
	d.log.Info("Derived deposits", "deposits", deposits, "l2Parent", l2Head, "l1Origin", l1Origin)
	for _, err := range errs {
		d.log.Error("Failed to derive a deposit", "l1OriginHash", l1Origin.Hash, "err", err)
	}
	// TODO: Should we halt if len(errs) > 0? Opens up a denial of service attack, but prevents lockup of funds.
```

## Snippet 2

Context: `opnode/rollup/driver/step.go:177` (changes a sensitive control or state-update path)

Before
```go
return l2Head, l2SafeHead, false, fmt.Errorf("failed to get L1 timestamp of next L1 block: %v", err)
	}
	deposits, err := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)
	if err != nil {
		return l2Head, l2SafeHead, false, fmt.Errorf("failed to derive deposits: %w", err)
	}
	// TODO: with sharding the blobs may be identified in more detail than L1 block hashes
	transactions, err := d.dl.FetchAllTransactions(fetchCtx, l1Input)
```
After
```go
return l2Head, l2SafeHead, false, fmt.Errorf("failed to get L1 timestamp of next L1 block: %v", err)
	}
	deposits, errs := derive.DeriveDeposits(receipts, d.Config.DepositContractAddress)
	for _, err := range errs {
		d.log.Error("Failed to derive a deposit", "l1OriginHash", l1Input[0].Hash, "err", err)
	}
	// TODO: Should we halt if len(errs) > 0? Opens up a denial of service attack, but prevents lockup of funds.
	// TODO: with sharding the blobs may be identified in more detail than L1 block hashes
```

## Snippet 3

Context: `opnode/rollup/derive/payload_attributes.go:344` (changes persisted or aggregate state handling)

Before
```go
}

func DeriveDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]hexutil.Bytes, error) {
	userDeposits, err := UserDeposits(receipts, depositContractAddr)
	if err != nil {
		return nil, fmt.Errorf("failed to derive user deposits: %v", err)
	}
	encodedTxs := make([]hexutil.Bytes, 0, len(userDeposits))
```
After
```go
}

func DeriveDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]hexutil.Bytes, []error) {
	userDeposits, errs := UserDeposits(receipts, depositContractAddr)
	encodedTxs := make([]hexutil.Bytes, 0, len(userDeposits))
	for i, tx := range userDeposits {
		opaqueTx, err := types.NewTx(tx).MarshalBinary()
		if err != nil {
```

## Snippet 4

Context: `opnode/rollup/derive/payload_attributes.go:202` (changes a sensitive control or state-update path)

Before
```go
// UserDeposits transforms the L2 block-height and L1 receipts into the transaction inputs for a full L2 block
func UserDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]*types.DepositTx, error) {
	var out []*types.DepositTx

	for _, rec := range receipts {
		if rec.Status != types.ReceiptStatusSuccessful {
			continue
```
After
```go
// UserDeposits transforms the L2 block-height and L1 receipts into the transaction inputs for a full L2 block
func UserDeposits(receipts []*types.Receipt, depositContractAddr common.Address) ([]*types.DepositTx, []error) {
	var out []*types.DepositTx
	var errs []error

	for i, rec := range receipts {
		if rec.Status != types.ReceiptStatusSuccessful {
```

# Fix Pattern

Replace batch-wide fail-fast parsing/encoding with per-item validation and error isolation, and constrain upstream field types to parser-supported ranges where possible.

## How It Was Fixed

The directly shown fix changes the deposit derivation API to return partial results plus an error list, then updates the driver to log individual derivation failures while continuing with valid deposits. The commit body describes an additional preventive change at the contract boundary by narrowing deposit `gasLimit` to a parser-compatible width, but that specific code change is not directly validated by the provided hunks.

# Why It Matters

1. One malformed deposit no longer aborts derivation for every deposit in the same L1 input batch.

2. The affected path is part of L1-to-L2 deposit ingestion, so fail-fast behavior there can disrupt rollup progress.

3. The fix isolates damage to the bad deposit entry instead of converting it into a broader availability failure.

4. The commit body explicitly discusses a denial-of-service tradeoff, which is consistent with the observed control-flow change.

# Evidence Notes

Strong direct evidence exists for the fail-fast to partial-success transition in `opnode/rollup/derive/payload_attributes.go` and for the driver no longer returning `failed to derive deposits` in `opnode/rollup/driver/step.go`. That is enough to support a likely availability-oriented security fix in deposit derivation. However, the claim about changing deposit `gasLimit` from `uint256` to `uint64` comes from the commit body and file list, not from the supplied code hunks, so it should be treated as supporting but not fully verified here. The provided evidence does not establish a historical exploit, universal exploitability, theft, or a demonstrated consensus split. Protocol security invariant: Malformed or unparsable L1 deposit entries must be isolated to the affected entry; they should not cause the opnode to abort derivation for the entire L1 input batch. Inputs accepted upstream should also fit the node parser's representable field widths. Verification notes: The patch does not prove that an untrusted user could trigger this path in every deployment configuration. The patch does not prove theft; the stated impact is chain halt or dropped deposits, with possible loss limited to the affected deposit path. The patch does not show a historical exploitation event or consensus split in production. The exact contract-side line for the `uint64` gasLimit change is mentioned in the commit body but not shown in the provided hunk evidence. Directly shown: `UserDeposits` and `DeriveDeposits` now return `[]error` instead of one fatal error. Directly shown: driver call sites now log deposit derivation errors and proceed instead of returning immediately. Not directly shown: the contract-side `gasLimit` type change mentioned in the commit body. The security conclusion is therefore supported but not fully proven from code alone, so confidence is medium rather than high. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `denial-of-service`
Final impact type: `availability`
Final confidence: `medium`
Final tags: `availability, malformed-input, error-isolation, rollup`

The patch evidence supports a security-relevant availability hardening change in deposit processing. Before the change, one malformed or unencodable deposit caused `DeriveDeposits` to fail fatally and the driver aborted block or epoch processing; after the change, bad deposits are isolated, logged, and skipped while valid deposits continue. That materially reduces a denial-of-service condition in a consensus-sensitive ingestion path. However, the supplied hunks do not fully prove attacker control or the exact upstream bug source described in the commit message, so this is better classified as security-hardening than a fully proven security-fix.

## Security Evidence

1. Before the patch, a single deposit derivation error caused `createNewBlock` and `insertEpoch` to return an error and stop processing.
2. After the patch, deposit derivation returns partial results plus `[]error`, allowing valid deposits to continue.
3. `UserDeposits` now records malformed deposit log errors per receipt/log instead of aborting the whole batch.
4. `DeriveDeposits` now records encoding failures per deposit instead of failing the entire derivation step.
5. The code comment explicitly notes the prior halt behavior exposed a denial-of-service tradeoff.

## Missing Evidence

1. The provided hunks do not show the claimed contract-side `gasLimit` narrowing from `uint256` to `uint64`.
2. The patch alone does not prove an external attacker could reliably trigger the malformed deposit condition in practice.
3. The evidence does not show exploitation, consensus break, or direct fund theft.

## Claim Boundaries

1. Supported: the patch reduces batch-wide failure from malformed deposit inputs in the deposit derivation path.
2. Supported: the security relevance is primarily availability/DoS resistance.
3. Not supported from the hunks alone: a concrete exploitable vulnerability with demonstrated attacker reachability.
4. Not supported from the hunks alone: the exact upstream input-validation flaw described in the commit message.
