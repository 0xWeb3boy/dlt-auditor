---
case_id: case_20250522_20ad4f500
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-05-22
source_refs:
  - git:20ad4f500e7fafab93f6d94fa171a5c0309de6ce
  - "core/txpool/validation.go:65"
  - "core/txpool/errors.go:59"
  - "core/txpool/blobpool/blobpool.go:63"
  - "core/txpool/validation.go:43"
bug_class: resource-exhaustion
impact_type:
  - denial-of-service
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - resource-limits
  - denial-of-service
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit per-transaction blob-count limit to txpool validation and sets a blobpool-specific cap of 7 blobs. That is evidence of resource-control hardening in blobpool admission, but the supplied material does not establish that the prior behavior was a concrete security bug rather than a robustness or policy gap.

## Observed Patch Facts

1. In `core/txpool/validation.go`, the patch adds `if blobCount := len(tx.BlobHashes()); blobCount > opts.MaxBlobCount {`.

2. In `core/txpool/errors.go`, the patch adds `// ErrTxBlobLimitExceeded is returned if a transaction would exceed the number`.

3. In `core/txpool/blobpool/blobpool.go`, the patch replaces `// maxTxsPerAccount is the maximum number of blob transactions admitted from` with `// maxBlobsPerTx is the maximum number of blobs that a single transaction can`.

4. In `core/txpool/validation.go`, the patch replaces `Accept uint8 // Bitmap of transaction types that should be accepted for the calling pool` with `Accept uint8 // Bitmap of transaction types that should be accepted for the calling pool`.

## Project Context

The changed code sits primarily in `core/txpool`, `core/txpool/blobpool`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/txpool/blobpool/blobpool_test.go`, `core/txpool/txpool.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/legacypool/legacypool.go`, `core/txpool/blobpool/slotter.go`. The strongest project-level identifiers around this patch are `transaction`, `pool`, `that`, and `limit`.

## Before/After Behavior

Before the patch, the shown validation path checked accepted transaction types and transaction size, but the provided snippets show no explicit `len(tx.BlobHashes())` limit in `ValidationOptions` or `ValidateTransaction`. After the patch, `ValidationOptions` gains `MaxBlobCount`, `ValidateTransaction` rejects transactions whose blob count exceeds that bound, `errors.go` adds `ErrTxBlobLimitExceeded`, and blobpool defines `maxBlobsPerTx = 7` as a local stability limit.

# Root Cause

A per-transaction blob-count limit was not explicitly enforced in the shared txpool validation inputs and admission path used by blobpool.

## Walkthrough

1. `core/txpool/validation.go` adds `MaxBlobCount` to `ValidationOptions`, so callers can provide a blob-count policy.

2. `core/txpool/validation.go` adds an early check rejecting transactions when `len(tx.BlobHashes()) > opts.MaxBlobCount`.

3. `core/txpool/errors.go` adds `ErrTxBlobLimitExceeded` to identify this rejection path.

4. `core/txpool/blobpool/blobpool.go` defines `maxBlobsPerTx = 7` and documents that the cap is chosen for network and txpool stability.

5. These changes show a txpool-local admission limit, not a consensus-rule change or an exploit demonstration.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/txpool/validation.go | 62 | shared transaction admission path now enforces a per-transaction blob-count limit before expensive validation |
| core/txpool/validation.go | 42 | validation options gain `MaxBlobCount`, wiring the new admission-control policy into callers |
| core/txpool/blobpool/blobpool.go | 57 | blobpool defines the local maximum blobs per transaction used to keep pool handling stable |
| core/txpool/errors.go | 53 | introduces a dedicated rejection reason for transactions exceeding the blob-count limit |

## Code Snippets

## Snippet 1

Context: `core/txpool/validation.go:65` (updates aggregate accounting or lifecycle state)

Before
```go
return fmt.Errorf("%w: tx type %v not supported by this pool", core.ErrTxTypeNotSupported, tx.Type())
	}
	// Before performing any expensive validations, sanity check that the tx is
	// smaller than the maximum limit the pool can meaningfully handle
```
After
```go
return fmt.Errorf("%w: tx type %v not supported by this pool", core.ErrTxTypeNotSupported, tx.Type())
	}
	if blobCount := len(tx.BlobHashes()); blobCount > opts.MaxBlobCount {
		return fmt.Errorf("%w: blob count %v, limit %v", ErrTxBlobLimitExceeded, blobCount, opts.MaxBlobCount)
	}
	// Before performing any expensive validations, sanity check that the tx is
	// smaller than the maximum limit the pool can meaningfully handle
```

## Snippet 2

Context: `core/txpool/errors.go:59` (updates aggregate accounting or lifecycle state)

Before
```go
ErrOversizedData = errors.New("oversized data")

	// ErrAlreadyReserved is returned if the sender address has a pending transaction
	// in a different subpool. For example, this error is returned in response to any
```
After
```go
ErrOversizedData = errors.New("oversized data")

	// ErrTxBlobLimitExceeded is returned if a transaction would exceed the number
	// of blobs allowed by blobpool.
	ErrTxBlobLimitExceeded = errors.New("transaction blob limit exceeded")

	// ErrAlreadyReserved is returned if the sender address has a pending transaction
	// in a different subpool. For example, this error is returned in response to any
```

## Snippet 3

Context: `core/txpool/blobpool/blobpool.go:63` (updates aggregate accounting or lifecycle state)

Before
```go
txMaxSize = 1024 * 1024

	// maxTxsPerAccount is the maximum number of blob transactions admitted from
	// a single account. The limit is enforced to minimize the DoS potential of
```
After
```go
txMaxSize = 1024 * 1024

	// maxBlobsPerTx is the maximum number of blobs that a single transaction can
	// carry. We choose a smaller limit than the protocol-permitted MaxBlobsPerBlock
	// in order to ensure network and txpool stability.
	// Note: if you increase this, validation will fail on txMaxSize.
	maxBlobsPerTx = 7
```

## Snippet 4

Context: `core/txpool/validation.go:43` (updates aggregate accounting or lifecycle state)

Before
```go
Config *params.ChainConfig // Chain configuration to selectively validate based on current fork rules

	Accept  uint8    // Bitmap of transaction types that should be accepted for the calling pool
	MaxSize uint64   // Maximum size of a transaction that the caller can meaningfully handle
	MinTip  *big.Int // Minimum gas tip needed to allow a transaction into the caller pool
}
```
After
```go
Config *params.ChainConfig // Chain configuration to selectively validate based on current fork rules

	Accept       uint8    // Bitmap of transaction types that should be accepted for the calling pool
	MaxSize      uint64   // Maximum size of a transaction that the caller can meaningfully handle
	MaxBlobCount int      // Maximum number of blobs allowed per transaction
	MinTip       *big.Int // Minimum gas tip needed to allow a transaction into the caller pool
}
```

# Fix Pattern

Add an explicit resource-limit field to shared validation options and enforce it early in admission with a dedicated error.

## How It Was Fixed

The fix introduces `MaxBlobCount` in the validation options, checks blob count in `ValidateTransaction` before later validation work, returns `ErrTxBlobLimitExceeded` on violation, and sets blobpool's concrete limit to 7 blobs per transaction.

# Why It Matters

1. Prevents blobpool from accepting transactions outside its intended local resource envelope.

2. Makes blob-count policy explicit instead of implicit or absent in shared validation.

3. Separates blob-count violations from generic oversized-data failures.

4. The evidence supports stability hardening, but not a proven exploitable vulnerability.

# Evidence Notes

The grounded evidence is limited to four visible changes: a new `MaxBlobCount` option, an early blob-count check in `ValidateTransaction`, a new `ErrTxBlobLimitExceeded` error, and blobpool's `maxBlobsPerTx = 7` constant with comments about network and txpool stability. The provided snippets do not show concrete pre-patch exhaustion behavior, attacker control analysis, consensus invalidity, privilege impact, or a documented security incident. Because the security thesis is inferential rather than established by the supplied evidence, classification is downgraded to unclear. Protocol security invariant: The transaction pool should apply its own explicit per-transaction resource limits during admission. This patch adds a blob-count bound for blobpool handling, but the provided evidence only shows a local stability policy, not a demonstrated exploitable vulnerability. Verification notes: The patch does not show that oversized blob transactions were consensus-invalid before this change. The patch does not prove remote exploitability or quantify pre-patch denial-of-service impact. The patch does not show memory, disk, or CPU exhaustion mechanics beyond adding a preventive admission limit. The evidence supports a txpool-local hardening measure, not chain compromise or authorization bypass. Confirmed the patch adds a new admission-time blob-count check. Confirmed the new limit is described as a txpool/blobpool stability policy. Did not find evidence in the supplied material of consensus impact or a demonstrated exploit. Did not find evidence quantifying pre-patch CPU, memory, disk, or network exhaustion. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, txpool, resource-limits, denial-of-service`

The patch adds an explicit per-transaction blob-count admission limit in the txpool/blobpool path and labels related size checks as DoS protection or stability controls. That is strong evidence of security-relevant hardening against resource abuse in a network-exposed transaction-processing subsystem. However, the supplied diff does not prove a concrete exploitable pre-patch vulnerability, real attack path, or measured exhaustion condition, so this should be retained as security hardening rather than a confirmed security bug fix.

## Security Evidence

1. `ValidateTransaction` now rejects transactions whose blob count exceeds `opts.MaxBlobCount` before further processing.
2. `ValidationOptions` gains `MaxBlobCount`, showing an explicit resource-control policy was added to admission logic.
3. A dedicated `ErrTxBlobLimitExceeded` error was introduced for this rejection path.
4. `blobpool.go` sets `maxBlobsPerTx = 7` and states the cap is chosen for network and txpool stability.
5. Nearby comments describe oversized transaction checks as DoS protection, placing this limit in a security-relevant resource-abuse context.

## Missing Evidence

1. No proof that pre-patch behavior was exploitable in practice.
2. No demonstrated memory, CPU, disk, or network exhaustion trace.
3. No advisory, CVE, or commit text explicitly calling this a security issue.
4. No evidence of consensus failure, privilege impact, or fund risk.

## Claim Boundaries

1. Supported claim: the patch hardens txpool admission against oversized blob-bearing transactions.
2. Supported claim: the change reduces resource-abuse exposure in a security-sensitive subsystem.
3. Not supported: a confirmed exploitable vulnerability existed before the patch.
4. Not supported: consensus compromise, state drift, or economic distortion from this issue.
