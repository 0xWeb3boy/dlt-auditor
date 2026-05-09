---
case_id: case_20201120_ff38a46af6
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: high
source_quality: high
date: 2020-11-20
source_refs:
  - git:ff38a46af60e5f2aacd7d8b4e88677eba3db8201
  - "runtime/src/bloom.rs:47"
  - "runtime/src/bloom.rs:4"
  - "core/src/crds_gossip_pull.rs:94"
  - "core/src/crds_gossip_pull.rs:100"
bug_class: remote-denial-of-service
impact_type:
  - availability
tags:
  - blockchain-core
  - gossip
  - bloom-filter
  - input-validation
  - denial-of-service
  - validator-panic
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a validator panic reachable through over-the-wire pull requests by making Bloom<T>::sanitize() reject empty bit vectors. The supported vulnerability is denial of service through malformed Bloom filter input causing division by zero, not state corruption, cryptographic bypass, arbitrary code execution, or a proven consensus safety failure.

## Observed Patch Facts

1. In `runtime/src/bloom.rs`, the patch replaces `impl<T: BloomHashIndex> solana_sdk::sanitize::Sanitize for Bloom<T> {}` with `impl<T: BloomHashIndex> Sanitize for Bloom<T> {`.

2. In `runtime/src/bloom.rs`, the patch changes a sensitive implementation path.

3. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn test_mask_u64(&self, item: u64, ones: u64) -> bool {` with `fn test_mask(&self, item: &Hash) -> bool {`.

4. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn add(&mut self, item: &Hash) {` with `#[cfg(test)]`.

## Project Context

The changed code sits primarily in `runtime/src`, `core/src`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/blockhash_queue.rs`, `runtime/src/bank.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `core/src/crds_value.rs`. The strongest project-level identifiers around this patch are `item`, `Hash`, `bits`, and `solana_sdk::sanitize::Sanitize`.

## Before/After Behavior

Before the patch, Bloom<T> used a default/no-op Sanitize implementation, so an empty bits vector could pass sanitization. The commit message states that pull requests received over the wire could then cause a validator panic via division by zero in bloom filters, and the added code comment identifies self.pos(...) as the protected downstream operation. After the patch, Bloom<T>::sanitize() returns SanitizeError::InvalidValue when self.bits.is_empty() and Ok(()) otherwise. The CRDS gossip pull changes narrow helper visibility or test scope, but the primary security behavior change is the Bloom sanitization check.

# Root Cause

Bloom<T> did not validate that its bits vector was non-empty at the sanitization boundary, allowing malformed serialized or received Bloom filters to reach arithmetic that assumes a positive bit length.

## Walkthrough

1. A gossip pull request received over the wire may include Bloom-backed filtering data.

2. Before this patch, Bloom<T> had no Bloom-specific sanitize() validation for self.bits.

3. An empty bits vector could therefore pass sanitization.

4. The commit message and new code comment tie that malformed state to division by zero in downstream Bloom position logic.

5. The patch rejects empty bit vectors with SanitizeError::InvalidValue before that logic can run.

6. The CRDS helper visibility/test-only changes are supporting cleanup and should not be treated as the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bloom.rs | 47 | Defines Bloom<T> sanitization; now rejects empty bit vectors before downstream bloom position calculations can divide by zero. |
| runtime/src/bloom.rs | 4 | Imports Sanitize and SanitizeError needed to implement explicit validation failure for malformed Bloom values. |
| core/src/crds_gossip_pull.rs | 94 | CRDS gossip pull filter masking path that uses Bloom-backed filtering for pull request behavior; helper visibility is narrowed. |
| core/src/crds_gossip_pull.rs | 100 | Makes add/contains test-only helpers, reducing public API surface but not itself proving a security invariant change. |

## Code Snippets

## Snippet 1

Context: `runtime/src/bloom.rs:47` (changes a sensitive control or state-update path)

Before
```rust
}

impl<T: BloomHashIndex> solana_sdk::sanitize::Sanitize for Bloom<T> {}

impl<T: BloomHashIndex> Bloom<T> {
```
After
```rust
}

impl<T: BloomHashIndex> Sanitize for Bloom<T> {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        // Avoid division by zero in self.pos(...).
        if self.bits.is_empty() {
            Err(SanitizeError::InvalidValue)
        } else {
```

## Snippet 2

Context: `runtime/src/bloom.rs:4` (changes a sensitive control or state-update path)

Before
```rust
use rand::{self, Rng};
use serde::{Deserialize, Serialize};
use std::fmt;
use std::sync::atomic::{AtomicU64, Ordering};
```
After
```rust
use rand::{self, Rng};
use serde::{Deserialize, Serialize};
use solana_sdk::sanitize::{Sanitize, SanitizeError};
use std::fmt;
use std::sync::atomic::{AtomicU64, Ordering};
```

## Snippet 3

Context: `core/src/crds_gossip_pull.rs:94` (changes signature or replay validation logic)

Before
```rust
u64::from_le_bytes(buf)
    }
    pub fn test_mask_u64(&self, item: u64, ones: u64) -> bool {
        let bits = item | ones;
        bits == self.mask
    }
    pub fn test_mask(&self, item: &Hash) -> bool {
        // only consider the highest mask_bits bits from the hash and set the rest to 1.
```
After
```rust
u64::from_le_bytes(buf)
    }
    fn test_mask(&self, item: &Hash) -> bool {
        // only consider the highest mask_bits bits from the hash and set the rest to 1.
        let ones = (!0u64).checked_shr(self.mask_bits).unwrap_or(!0u64);
```

## Snippet 4

Context: `core/src/crds_gossip_pull.rs:100` (changes signature or replay validation logic)

Before
```rust
bits == self.mask
    }
    pub fn add(&mut self, item: &Hash) {
        if self.test_mask(item) {
            self.filter.add(item);
        }
    }
    pub fn contains(&self, item: &Hash) -> bool {
```
After
```rust
bits == self.mask
    }
    #[cfg(test)]
    fn add(&mut self, item: &Hash) {
        if self.test_mask(item) {
            self.filter.add(item);
        }
    }
```

# Fix Pattern

Validate untrusted structured input at the sanitize boundary and reject impossible internal dimensions before arithmetic depends on them.

## How It Was Fixed

runtime/src/bloom.rs now imports Sanitize and SanitizeError and replaces the empty Sanitize implementation with an explicit sanitize() method. That method rejects Bloom filters whose bits vector is empty. Related CRDS gossip pull helper methods were made private or test-only, but the evidenced vulnerability fix is the non-empty Bloom bits check.

# Why It Matters

1. Prevents malformed over-the-wire pull requests from panicking a validator.

2. Enforces the concrete invariant required by Bloom position/index arithmetic.

3. Supports a denial-of-service classification only.

4. Does not establish ledger corruption, signature bypass, arbitrary code execution, or consensus violation.

# Evidence Notes

Primary evidence is runtime/src/bloom.rs where the no-op Sanitize implementation is replaced by explicit validation of self.bits.is_empty(), returning SanitizeError::InvalidValue. The commit message directly states that pull requests received over the wire can cause validator panic because of division by zero in bloom filters. The CRDS gossip pull hunks show related helper visibility and test-scope changes, but they do not independently establish the vulnerability. Claims about storage state corruption or cryptographic/replay-sensitive logic are unsupported by the provided evidence. Protocol security invariant: Bloom filters accepted through the gossip pull request path must have a non-empty bit vector before any downstream position/index calculation uses the bit-vector length as a divisor. Verification notes: The patch proves a validator panic risk from malformed over-the-wire bloom filters, not arbitrary code execution. The evidence does not show ledger state corruption or consensus safety violation. The CRDS helper visibility changes look like cleanup or test-scope tightening, not the primary security fix. The patch does not prove bypass of cryptographic validation or signature checks. The exact network reachability and attacker prerequisites are not fully shown beyond pull requests received over the wire. Confirmed by commit message naming over-the-wire pull requests and division-by-zero validator panic. Confirmed by code change rejecting empty Bloom bit vectors during sanitization. No evidence provided for arbitrary code execution, cryptographic bypass, ledger state corruption, or exact attacker prerequisites beyond over-the-wire pull requests. No test evidence was provided in the input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `remote-denial-of-service`
Final impact type: `availability`
Final tags: `blockchain-core, gossip, bloom-filter, input-validation, denial-of-service, validator-panic`

The provided evidence supports retaining this as a security fix, but only as a remotely reachable denial-of-service fix. The commit message states that pull requests received over the wire could cause a validator panic through division by zero in bloom filters, and the patch adds explicit sanitization rejecting empty Bloom bit vectors before downstream position arithmetic. The original state-corruption, storage, snapshot, queue, and signature framing is not supported by the supplied patch evidence.

## Security Evidence

1. Commit message identifies over-the-wire pull requests as the source of malformed input.
2. Commit message names validator panic due to division by zero in bloom filters.
3. Patch replaces a no-op Bloom<T> Sanitize implementation with validation that rejects empty bits vectors.
4. New code comment directly ties the check to avoiding division by zero in self.pos(...).
5. Rejecting malformed serialized Bloom state at sanitize time is a security-relevant availability fix for validator software.

## Missing Evidence

1. No supplied evidence shows ledger state corruption or state-integrity impact.
2. No supplied evidence shows signature verification bypass, replay bypass, or cryptographic failure.
3. No supplied evidence proves consensus safety failure beyond validator panic availability risk.
4. Exact attacker prerequisites beyond over-the-wire pull requests are not fully shown.
5. No test evidence is provided.

## Claim Boundaries

1. Classify as denial of service through malformed Bloom filter input, not state corruption.
2. Impact is validator availability, not ledger integrity or arbitrary code execution.
3. The CRDS helper visibility and test-scope changes are supporting cleanup unless tied more directly to the panic path.
4. The supported root cause is missing validation of non-empty Bloom bits at the sanitize boundary.
