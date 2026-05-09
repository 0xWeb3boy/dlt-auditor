---
case_id: case_20201120_0ad7b64961
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2020-11-20
source_refs:
  - git:0ad7b649616a4754a9c50171c66786c46a22fa2f
  - "runtime/src/bloom.rs:47"
  - "runtime/src/bloom.rs:4"
  - "core/src/crds_gossip_pull.rs:93"
  - "core/src/crds_gossip_pull.rs:99"
bug_class: missing-input-validation
impact_type:
  - denial-of-service
confidence: high
tags:
  - blockchain-core
  - gossip
  - bloom-filter
  - input-validation
  - remote-input
  - panic
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch adds explicit sanitization for Bloom filters used in Solana gossip pull handling. Previously, `Bloom<T>` had a default no-op `Sanitize` implementation, allowing an empty `bits` vector to pass validation. The commit message states that over-the-wire pull requests could trigger a validator panic through division by zero in Bloom filter logic. The fix rejects empty Bloom filters with `SanitizeError::InvalidValue`.

## Observed Patch Facts

1. In `runtime/src/bloom.rs`, the patch replaces `impl<T: BloomHashIndex> solana_sdk::sanitize::Sanitize for Bloom<T> {}` with `impl<T: BloomHashIndex> Sanitize for Bloom<T> {`.

2. In `runtime/src/bloom.rs`, the patch changes a sensitive implementation path.

3. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn test_mask_u64(&self, item: u64, ones: u64) -> bool {` with `fn test_mask(&self, item: &Hash) -> bool {`.

4. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn add(&mut self, item: &Hash) {` with `#[cfg(test)]`.

## Project Context

The changed code sits primarily in `runtime/src`, `core/src`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/blockhash_queue.rs`, `runtime/src/bank.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `core/src/crds_value.rs`. The strongest project-level identifiers around this patch are `item`, `Hash`, `bits`, and `solana_sdk::sanitize::Sanitize`.

## Before/After Behavior

Before the patch, deserialized `Bloom<T>` values satisfied `Sanitize` through an empty implementation, so `self.bits.is_empty()` was not rejected before downstream Bloom position calculations. After the patch, `runtime/src/bloom.rs` implements `sanitize()` explicitly and returns `Err(SanitizeError::InvalidValue)` when `self.bits` is empty, otherwise `Ok(())`. The `core/src/crds_gossip_pull.rs` changes narrow helper visibility and make some helpers test-only, but the supplied evidence does not show those changes are the root security fix.

# Root Cause

Missing validation at the wire-input sanitization boundary for Bloom filters. A malformed Bloom filter with an empty bit vector could be accepted and later used by Bloom position logic that depended on the bit-vector length, leading to division by zero and validator panic.

## Walkthrough

1. A CRDS gossip pull request received over the wire can include Bloom filter data used by the pull filtering path.

2. Before the patch, `Bloom<T>` implemented `Sanitize` with the default empty implementation, so sanitization did not reject empty `bits`.

3. The commit message states that this malformed input could cause a validator panic by division by zero in Bloom filter logic.

4. The patch replaces the no-op implementation with a concrete `sanitize()` method.

5. The new method rejects Bloom filters whose `bits` vector is empty by returning `SanitizeError::InvalidValue`.

6. Malformed Bloom filters are therefore rejected before downstream Bloom position calculations can run on a zero-length bit vector.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bloom.rs | 4 | imports Sanitize and SanitizeError so Bloom can enforce a concrete validation rule |
| runtime/src/bloom.rs | 47 | rejects Bloom filters with empty bits before operations that can divide by the bit-vector length |
| core/src/crds_gossip_pull.rs | 93 | CRDS pull filter mask matching path that consumes hashes and the Bloom-backed filter during gossip pull handling |
| core/src/crds_gossip_pull.rs | 99 | limits add/contains helper exposure to tests, reducing public API surface but not itself proving a security fix |

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

Context: `core/src/crds_gossip_pull.rs:93` (changes signature or replay validation logic)

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

Context: `core/src/crds_gossip_pull.rs:99` (changes signature or replay validation logic)

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

Replace default/no-op protocol data sanitization with an explicit structural invariant check that rejects malformed input before downstream calculations depend on invalid dimensions.

## How It Was Fixed

`runtime/src/bloom.rs` now imports `Sanitize` and `SanitizeError` and implements `Sanitize for Bloom<T>` with a concrete `sanitize()` method. The method rejects empty `bits` vectors as `SanitizeError::InvalidValue`. The CRDS helper visibility changes are treated as secondary cleanup or surface reduction, not the primary demonstrated vulnerability fix.

# Why It Matters

1. Prevents malformed gossip pull Bloom filters from triggering division by zero.

2. Addresses a validator panic reachable from over-the-wire pull requests, according to the commit message.

3. Supports denial-of-service classification, not memory corruption or consensus corruption.

4. Keeps the security claim scoped to input validation for remote panic prevention.

# Evidence Notes

Primary evidence is the `runtime/src/bloom.rs` change from a no-op `Sanitize` implementation to an explicit check rejecting `self.bits.is_empty()`, with an inline comment saying it avoids division by zero in `self.pos(...)`. The commit body states that pull requests received over the wire can cause a validator panic because of division by zero in Bloom filters. Evidence for `core/src/crds_gossip_pull.rs` shows helper visibility and test-only changes, but does not independently establish a vulnerability. No supplied evidence supports claims of arbitrary memory corruption, authentication bypass, signature bypass, ledger corruption, or broader consensus safety impact. Protocol security invariant: CRDS gossip pull requests received over the wire must reject malformed Bloom filters before any membership or hash-position calculation. A deserialized Bloom filter must have a non-empty bit vector so downstream position logic cannot divide by zero and panic the validator. Verification notes: The patch proves prevention of a validator panic from empty Bloom filter bits, not arbitrary memory corruption. The evidence does not show consensus state corruption or ledger safety impact. The CRDS helper visibility changes alone are not evidence of a vulnerability. The patch does not prove authentication bypass, signature bypass, or cryptographic weakness. Exploitability beyond sending malformed over-the-wire pull requests is not established by the provided evidence. Confirmed by commit message naming over-the-wire pull requests, validator panic, and division by zero. Confirmed by code change rejecting empty Bloom bit vectors during sanitization. CRDS helper changes should not be treated as the root cause based on supplied evidence. Exploitability is established only as remote malformed-input validator panic, not broader compromise. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-input-validation`
Final impact type: `denial-of-service`
Final confidence: `high`
Final tags: `blockchain-core, gossip, bloom-filter, input-validation, remote-input, panic, denial-of-service`

The supplied commit message and patch evidence strongly support a security-relevant fix: over-the-wire gossip pull requests could provide a malformed Bloom filter with empty bits, pass a no-op Sanitize implementation, and later trigger division by zero causing validator panic. The patch adds explicit sanitization rejecting empty Bloom filters. The original finding is directionally correct but its storage/state-corruption/state-integrity/snapshot/signature framing is unsupported and should be narrowed to remote malformed-input denial of service.

## Security Evidence

1. Commit body states pull requests received over the wire can cause a validator panic via division by zero in Bloom filters.
2. Bloom<T> previously had a no-op Sanitize implementation.
3. Patch adds sanitize() and rejects self.bits.is_empty() with SanitizeError::InvalidValue.
4. Inline code comment explicitly says the check avoids division by zero in self.pos(...).

## Missing Evidence

1. No evidence of state corruption, ledger integrity impact, or consensus safety failure.
2. No evidence of signature, authentication, or cryptographic bypass.
3. No evidence that the CRDS helper visibility changes are independently security-critical.

## Claim Boundaries

1. Validated only as remote malformed-input validator panic prevention.
2. Impact should be scoped to denial of service, not state integrity or storage corruption.
3. Primary fix is Bloom filter sanitization; CRDS helper visibility changes are secondary cleanup from the supplied evidence.
