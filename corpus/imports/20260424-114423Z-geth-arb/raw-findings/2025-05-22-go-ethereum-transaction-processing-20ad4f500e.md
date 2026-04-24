---
case_id: case_20250522_20ad4f500e
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2025-05-22
source_refs:
  - git:20ad4f500e7fafab93f6d94fa171a5c0309de6ce
  - "core/txpool/validation.go:65"
  - "core/txpool/errors.go:59"
  - "core/txpool/blobpool/blobpool.go:63"
  - "core/txpool/validation.go:43"
bug_class: resource-control-missing-limit
impact_type:
  - availability
  - resource-exhaustion
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - blobpool
  - resource-control
  - dos-hardening
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit per-transaction blob-count limit to go-ethereum's txpool/blobpool admission path. It extends `ValidationOptions` with `MaxBlobCount`, rejects transactions whose `len(tx.BlobHashes())` exceeds that configured limit, adds `ErrTxBlobLimitExceeded`, and defines blobpool's cap as `maxBlobsPerTx = 7`. The comments tie the limit to network and txpool stability. This supports a resource-control hardening finding, but not stronger claims such as consensus-invalid acceptance, storage corruption, remote crash, or accounting drift.

## Observed Patch Facts

1. In `core/txpool/validation.go`, the patch adds `if blobCount := len(tx.BlobHashes()); blobCount > opts.MaxBlobCount {`.

2. In `core/txpool/errors.go`, the patch adds `// ErrTxBlobLimitExceeded is returned if a transaction would exceed the number`.

3. In `core/txpool/blobpool/blobpool.go`, the patch replaces `// maxTxsPerAccount is the maximum number of blob transactions admitted from` with `// maxBlobsPerTx is the maximum number of blobs that a single transaction can`.

4. In `core/txpool/validation.go`, the patch replaces `Accept uint8 // Bitmap of transaction types that should be accepted for the calling pool` with `Accept uint8 // Bitmap of transaction types that should be accepted for the calling pool`.

## Project Context

The changed code sits primarily in `core/txpool`, `core/txpool/blobpool`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/txpool/blobpool/blobpool_test.go`, `core/txpool/txpool.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/legacypool/legacypool.go`, `core/txpool/blobpool/slotter.go`. The strongest project-level identifiers around this patch are `transaction`, `pool`, `that`, and `limit`.

## Before/After Behavior

Before the patch, the supplied `ValidateTransaction` evidence shows transaction type acceptance followed by the transaction size check, with no visible blob-count admission check. `ValidationOptions` had no `MaxBlobCount` field, and there was no dedicated excessive-blob-count error. After the patch, validation options include `MaxBlobCount`, `ValidateTransaction` rejects over-limit blob transactions early with `ErrTxBlobLimitExceeded`, and blobpool defines `maxBlobsPerTx = 7` as a stability-oriented cap below the protocol-permitted block blob limit.

# Root Cause

The common transaction validation path did not expose or enforce an explicit per-transaction blob-count bound for blobpool admission in the provided pre-patch evidence. That left the blobpool resource policy outside the early validation contract.

## Walkthrough

1. Blobpool already had a transaction size cap in the shown context, but no visible per-transaction blob-count cap before the patch.

2. `ValidationOptions` previously carried accepted transaction types, maximum transaction size, and minimum tip, but no blob-count limit.

3. `ValidateTransaction` previously proceeded from transaction type acceptance toward size and later validation without the shown blob-count check.

4. The patch adds `MaxBlobCount int` to `ValidationOptions`.

5. The patch adds an early `len(tx.BlobHashes()) > opts.MaxBlobCount` check in `ValidateTransaction`.

6. Over-limit transactions now fail with `ErrTxBlobLimitExceeded`.

7. Blobpool defines `maxBlobsPerTx = 7`, with comments stating the cap is below the protocol-permitted block blob limit for network and txpool stability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/txpool/validation.go | 43 | adds MaxBlobCount to transaction validation options so pools can configure a per-transaction blob limit |
| core/txpool/validation.go | 65 | rejects transactions whose blob hash count exceeds the configured maximum before later validation |
| core/txpool/errors.go | 59 | adds a specific admission error for transactions exceeding the blob count limit |
| core/txpool/blobpool/blobpool.go | 63 | defines blobpool's explicit maxBlobsPerTx resource cap for stability |

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

Add an explicit admission-time resource bound to shared validation options, enforce it before later validation work, and return a dedicated error when the bound is exceeded.

## How It Was Fixed

The fix introduced `MaxBlobCount` in `core/txpool/validation.go`, added an early blob-hash-count check in `ValidateTransaction`, added `ErrTxBlobLimitExceeded` in `core/txpool/errors.go`, and defined blobpool's concrete cap as `maxBlobsPerTx = 7` in `core/txpool/blobpool/blobpool.go`.

# Why It Matters

1. Enforces blobpool resource policy during transaction admission.

2. Rejects over-limit blob transactions before later validation work.

3. Keeps this limit distinct from consensus validity, since the cap is below the protocol-permitted block limit.

4. Provides a specific error for caller handling and tests.

5. The evidence supports stability and DoS-resistance hardening, not a proven exploit.

# Evidence Notes

Grounded evidence comes from `core/txpool/validation.go` adding `MaxBlobCount` and the `len(tx.BlobHashes())` check, `core/txpool/errors.go` adding `ErrTxBlobLimitExceeded`, and `core/txpool/blobpool/blobpool.go` defining `maxBlobsPerTx = 7` with comments about network and txpool stability. Unsupported claims about accounting drift, phantom state, storage corruption, consensus-invalid transaction acceptance, remote crash, or permanent denial of service are excluded. Protocol security invariant: Blobpool transaction admission should enforce an explicit caller-configured maximum number of blobs per transaction before later validation or pool handling. The evidence supports this as a txpool/network resource-control invariant, not as a consensus-validity invariant. Verification notes: No concrete exploit path is proven by the patch evidence. No consensus-invalid transaction acceptance is shown; the limit is described as smaller than the protocol-permitted MaxBlobsPerBlock. No state accounting drift, phantom state, or storage corruption is supported by the provided diff. No remote crash or permanent denial of service is demonstrated, only a resource-control gap is addressed. No concrete exploit path is proven by the supplied evidence. No consensus-invalid transaction acceptance is shown. No state accounting drift or storage corruption is supported. The change is security-relevant as resource-control hardening, but confidence is medium because the vulnerability impact is not fully demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-control-missing-limit`
Final impact type: `availability, resource-exhaustion`
Final tags: `blockchain-core, transaction-processing, txpool, blobpool, resource-control, dos-hardening, availability`

The supplied patch evidence supports a security-hardening classification: transaction admission now enforces an explicit maximum blob count before later validation and returns a dedicated error for over-limit blob transactions. The project context and comments tie the limit to blobpool/network stability, which is a resource-control and DoS-resistance concern. The original accounting, economic distortion, and consensus-oriented metadata is too strong for the provided evidence.

## Security Evidence

1. ValidateTransaction now rejects transactions where len(tx.BlobHashes()) exceeds opts.MaxBlobCount.
2. ValidationOptions now exposes a MaxBlobCount policy knob for callers such as blobpool.
3. A dedicated ErrTxBlobLimitExceeded error was added for excessive blob count admission failures.
4. The finding states blobpool defines maxBlobsPerTx = 7 with comments about network and txpool stability.

## Missing Evidence

1. No exploit path or attacker workflow is shown.
2. No evidence shows consensus-invalid transactions were accepted before the patch.
3. No evidence shows state accounting drift, storage corruption, or economic distortion.
4. No benchmark or failure trace demonstrates concrete resource exhaustion impact.

## Claim Boundaries

1. This should be kept as resource-control hardening, not a proven vulnerability fix.
2. Do not claim consensus safety, state accounting, or economic integrity impact from the supplied patch alone.
3. The supported impact is availability-oriented DoS-resistance for txpool/blobpool admission.
4. The evidence supports an explicit policy limit being added, not proof of a remote crash or permanent denial of service.
