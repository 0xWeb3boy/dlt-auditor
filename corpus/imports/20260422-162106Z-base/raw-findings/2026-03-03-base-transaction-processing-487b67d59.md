---
case_id: case_20260303_487b67d59
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: input-validation
impact_type:
  - correctness-or-hardening
confidence: low
source_quality: medium
tags:
  - blockchain-core
  - transaction-processing
  - input-validation
  - correctness-or-hardening
  - queue
  - consensus
date: 2026-03-03
source_refs:
  - git:487b67d59c6f21ee0e4f6667fd37d976757867ce
  - "crates/consensus/derive/src/sources/blobs.rs:163"
  - "crates/consensus/derive/src/errors/pipeline.rs:346"
  - "crates/consensus/derive/src/errors/sources.rs:39"
  - "crates/consensus/derive/src/sources/blobs.rs:13"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a post-processing consistency check in the blob-loading path: after filling blob-backed data, it now errors if any fetched blobs remain unused. That is a real correctness/integrity guard in a consensus-sensitive path, but the provided evidence does not establish a concrete vulnerability, attacker-controlled exploit path, or prior consensus break.

## Observed Patch Facts

1. In `crates/consensus/derive/src/sources/blobs.rs`, the patch replaces `self.data = data;` with `// Check for over-fill: ensure all blobs were consumed.`.

2. In `crates/consensus/derive/src/errors/pipeline.rs`, the patch adds `/// Blobs over-fill: expected fewer blobs than were fetched.`.

3. In `crates/consensus/derive/src/errors/sources.rs`, the patch adds `/// Reset error from blob loading.`.

4. In `crates/consensus/derive/src/sources/blobs.rs`, the patch replaces `PipelineError, PipelineResult,` with `PipelineError, PipelineResult, ResetError,`.

## Project Context

The changed code sits primarily in `crates/consensus/derive/src/sources`, `crates/consensus/derive/src`, `crates/consensus/derive/src/errors`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/consensus/derive/src/sources/blob_data.rs`, `crates/consensus/derive/src/sources/variant.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/derive/src/metrics/mod.rs`, `crates/consensus/derive/src/sources/blob_data.rs`. The strongest project-level identifiers around this patch are `blobs`, `error`, `expected`, and `ResetError::BlobsOverFill`.

## Before/After Behavior

Before the patch, `load_blobs` fetched and validated blobs, ran `blob.fill(&blobs, blob_index)` across the extracted data, and then continued into the success path without checking whether all fetched blobs had been consumed. After the patch, it rejects the case `blob_index < blobs.len()` with `ResetError::BlobsOverFill(...)`, and the new reset condition is propagated through `BlobProviderError`.

# Root Cause

The shown pre-fix code tracked consumed blob count with `blob_index` but lacked a final exact-consumption validation, so a mismatch between consumed blobs and fetched blobs was tolerated instead of being surfaced as an error.

## Walkthrough

1. `load_blobs` extracts `data` and `blob_hashes` from block transactions.

2. If blob hashes exist, it fetches and validates the corresponding `blobs`.

3. It iterates through `data` and calls `blob.fill(&blobs, blob_index)`, incrementing `blob_index` when a blob is consumed.

4. In the pre-fix path shown, execution then moved directly to the normal success path.

5. The patch adds a guard that returns `ResetError::BlobsOverFill(blob_index, blobs.len())` when validated blobs remain unused.

6. `ResetError::BlobsOverFill` is added in the pipeline error enum, and `BlobProviderError::Reset(#[from] ResetError)` is added so this condition propagates out of blob loading.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/consensus/derive/src/sources/blobs.rs | 118 | Primary derivation data-loading path that fetches blobs, fills blob-backed inputs, and now rejects surplus blobs after fill. |
| crates/consensus/derive/src/errors/pipeline.rs | 340 | Introduces the explicit reset/invariant error `BlobsOverFill` used when fetched blob count exceeds consumed blob count. |
| crates/consensus/derive/src/errors/sources.rs | 33 | Propagates blob-loading reset failures through `BlobProviderError`, making the new invariant violation observable to the pipeline. |

## Code Snippets

## Snippet 1

Context: `crates/consensus/derive/src/sources/blobs.rs:163` (changes a sensitive control or state-update path)

Before
```rust
}

        self.open = true;
        self.data = data;
```
After
```rust
}

        // Check for over-fill: ensure all blobs were consumed.
        if blob_index < blobs.len() {
            return Err(ResetError::BlobsOverFill(blob_index, blobs.len()).into());
        }

        self.open = true;
```

## Snippet 2

Context: `crates/consensus/derive/src/errors/pipeline.rs:346` (changes a sensitive control or state-update path)

Before
```rust
#[error("Next L1 block hash mismatch: expected {0}, got {1}")]
    NextL1BlockHashMismatch(B256, B256),
}
```
After
```rust
#[error("Next L1 block hash mismatch: expected {0}, got {1}")]
    NextL1BlockHashMismatch(B256, B256),
    /// Blobs over-fill: expected fewer blobs than were fetched.
    /// The first argument is the expected blob index, and the second argument is the actual blob count.
    #[error("Blobs over-fill: expected {0} blobs, got {1}")]
    BlobsOverFill(usize, usize),
}
```

## Snippet 3

Context: `crates/consensus/derive/src/errors/sources.rs:39` (changes a sensitive control or state-update path)

Before
```rust
#[error("{0}")]
    Backend(String),
}
```
After
```rust
#[error("{0}")]
    Backend(String),
    /// Reset error from blob loading.
    #[error("{0}")]
    Reset(#[from] ResetError),
}
```

## Snippet 4

Context: `crates/consensus/derive/src/sources/blobs.rs:13` (changes a sensitive control or state-update path)

Before
```rust
use crate::{
    BlobData, BlobProvider, BlobProviderError, ChainProvider, DataAvailabilityProvider,
    PipelineError, PipelineResult,
};
```
After
```rust
use crate::{
    BlobData, BlobProvider, BlobProviderError, ChainProvider, DataAvailabilityProvider,
    PipelineError, PipelineResult, ResetError,
};
```

# Fix Pattern

Add an explicit post-parse invariant check and propagate the failure through typed error paths.

## How It Was Fixed

The fix adds a leftover-blob check after the fill loop in `crates/consensus/derive/src/sources/blobs.rs`, introduces `ResetError::BlobsOverFill(usize, usize)` in `crates/consensus/derive/src/errors/pipeline.rs`, and wires reset propagation through `BlobProviderError` in `crates/consensus/derive/src/errors/sources.rs`.

# Why It Matters

1. It prevents silent acceptance of a blob-count mismatch in derivation input handling.

2. It makes the mismatch observable as an explicit reset/error instead of implicit success.

3. It strengthens a determinism/integrity check in a consensus-sensitive code path.

4. The evidence does not show memory corruption, resource bounding before fetch, or a demonstrated exploit.

# Evidence Notes

Grounded evidence is limited to the added post-loop check for `blob_index < blobs.len()`, the new `ResetError::BlobsOverFill` error variant, and propagation through `BlobProviderError::Reset`. The diff supports a logical consistency or integrity hardening interpretation. It does not by itself prove that valid on-chain input could trigger the condition, that an attacker could exploit it, that resource exhaustion was the issue, or that a consensus failure previously occurred. Protocol security invariant: When derivation loads blobs for a block, the fetched and validated blob set should match what the batch data actually consumes exactly; leftover validated blobs should be rejected rather than silently ignored. Verification notes: The patch does not show memory corruption or an out-of-bounds access; it adds a logical consistency check. The patch does not prove that an external attacker can force overfill through valid on-chain data; the mismatch could also arise from backend or blob-fetcher behavior. The patch does not support a strong resource-exhaustion claim, because the new check happens after blob fetch/validation rather than before allocation. The patch does not prove prior consensus divergence occurred; it shows that surplus blobs were previously tolerated instead of rejected. Assessment is based only on the provided diff snippets and summaries. No test changes or reproducer were provided to show the bug in action. No evidence was provided that the mismatch is externally triggerable through valid protocol data. Security relevance is plausible because the path is derivation-sensitive, but the vulnerability thesis is not established from the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The patch adds an exact-consumption check in blob loading and converts surplus validated blobs into an explicit reset error in a consensus-sensitive derivation path. That is a meaningful integrity hardening change because previously tolerated blob-count mismatches are now rejected instead of silently accepted. However, the supplied evidence does not prove a concrete exploitable vulnerability, attacker-controlled trigger, or prior consensus failure, so this is better retained as security hardening rather than a confirmed security bug fix.

## Security Evidence

1. `load_blobs` now returns `ResetError::BlobsOverFill` when fetched blobs remain unused after fill, enforcing an exact-match invariant.
2. A new `ResetError::BlobsOverFill(usize, usize)` variant was added specifically to represent the mismatch condition.
3. `BlobProviderError` now propagates reset errors from blob loading, making the invariant violation observable instead of allowing implicit success.
4. The affected code is in consensus/derivation blob handling, where deterministic input validation is security-sensitive.

## Missing Evidence

1. No reproducer or test shows that the mismatch was reachable from valid protocol data.
2. No evidence shows an external attacker could force the overfill condition rather than it arising from backend inconsistency.
3. No evidence shows prior consensus divergence, privilege bypass, memory corruption, or resource-exhaustion impact.

## Claim Boundaries

1. The diff supports an integrity hardening interpretation in a consensus-sensitive path, not proof of a concrete exploitable vulnerability.
2. The patch should not be described as fixing memory safety, authentication, or authorization issues.
3. The evidence does not justify claiming attacker-triggerable consensus break; it only shows previously silent surplus blobs are now rejected.
