---
case_id: case_20201119_a8c29505f0
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
date: 2020-11-19
source_refs:
  - git:a8c29505f0705a89c99e40369bcb4777a7e46f72
  - "runtime/src/bloom.rs:47"
  - "runtime/src/bloom.rs:4"
  - "core/src/crds_gossip_pull.rs:94"
  - "core/src/crds_gossip_pull.rs:100"
bug_class: panic-dos
impact_type:
  - availability
tags:
  - blockchain-core
  - gossip
  - input-validation
  - bloom-filter
  - panic
  - denial-of-service
  - network-input
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is a confirmed security fix for a remotely triggerable validator panic in Solana gossip pull handling. The evidence shows Bloom<T> sanitization changed from a no-op to rejecting empty bit vectors, matching the commit message that over-the-wire pull requests could cause division by zero in bloom filters.

## Observed Patch Facts

1. In `runtime/src/bloom.rs`, the patch replaces `impl<T: BloomHashIndex> solana_sdk::sanitize::Sanitize for Bloom<T> {}` with `impl<T: BloomHashIndex> Sanitize for Bloom<T> {`.

2. In `runtime/src/bloom.rs`, the patch changes a sensitive implementation path.

3. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn test_mask_u64(&self, item: u64, ones: u64) -> bool {` with `fn test_mask(&self, item: &Hash) -> bool {`.

4. In `core/src/crds_gossip_pull.rs`, the patch replaces `pub fn add(&mut self, item: &Hash) {` with `#[cfg(test)]`.

## Project Context

The changed code sits primarily in `runtime/src`, `core/src`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/blockhash_queue.rs`, `runtime/src/bank.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `core/src/crds_value.rs`. The strongest project-level identifiers around this patch are `item`, `Hash`, `bits`, and `solana_sdk::sanitize::Sanitize`.

## Before/After Behavior

Before the patch, Bloom<T> implemented Sanitize with an empty/default implementation, so an empty bits vector was not rejected. After the patch, Bloom<T>::sanitize returns SanitizeError::InvalidValue when self.bits.is_empty() and Ok(()) otherwise. The supplied CRDS gossip pull changes appear adjacent cleanup around helper visibility and test-only methods, not the root security fix.

# Root Cause

Bloom<T> lacked validation for the invariant that its bit vector must be non-empty. Malformed over-the-wire pull request data could therefore pass sanitization and later reach Bloom position logic that divides by the bit vector length, causing division by zero and a validator panic.

## Walkthrough

1. A CRDS gossip pull request is received over the wire with Bloom filter data.

2. Before the fix, Bloom<T>'s Sanitize implementation did not perform Bloom-specific checks.

3. An empty Bloom bits vector could therefore pass sanitization.

4. Later Bloom position calculation assumed a non-empty bit vector.

5. Using an empty vector length could trigger division by zero and panic the validator.

6. The patch adds Bloom<T>::sanitize and rejects empty bits with SanitizeError::InvalidValue.

7. The CRDS gossip pull helper changes are not independently established as security fixes by the supplied evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bloom.rs | 47 | Implements Bloom<T>::sanitize to reject empty bit vectors before Bloom position calculations can divide by zero. |
| runtime/src/bloom.rs | 4 | Imports Sanitize and SanitizeError needed for explicit validation failure. |
| core/src/crds_gossip_pull.rs | 92 | CRDS gossip pull filter path that uses hashes and bloom filtering for pull request behavior; changed helper visibility around mask testing. |
| core/src/crds_gossip_pull.rs | 100 | Restricts add/contains helpers to tests, indicating adjacent cleanup rather than the primary security fix. |

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

Enforce structural invariants during sanitization of network-controlled data before arithmetic assumes those invariants hold.

## How It Was Fixed

runtime/src/bloom.rs imports Sanitize and SanitizeError and replaces the empty Sanitize implementation for Bloom<T> with a concrete sanitize() method. The method rejects empty bit vectors and accepts non-empty ones.

# Why It Matters

1. Prevents malformed gossip pull input from triggering a validator panic.

2. Bounds the supported impact to availability denial of service, not memory corruption or consensus compromise.

3. Moves the check to sanitization before unsafe arithmetic assumptions are reached.

# Evidence Notes

The strongest evidence is runtime/src/bloom.rs line 47, where the empty Sanitize implementation is replaced with a check for self.bits.is_empty(). The added comment explicitly says this avoids division by zero in self.pos(...). The commit message states that pull requests received over the wire can cause a validator panic because of division by zero in bloom filters. core/src/crds_gossip_pull.rs changes show adjacent gossip pull filter code and helper visibility changes, but do not establish a separate cryptographic or replay-sensitive vulnerability. Protocol security invariant: Gossip pull requests received over the wire must not carry a Bloom filter with an empty bit vector, because downstream Bloom position calculation assumes a non-empty bit vector and can divide by zero otherwise. Verification notes: The patch does not prove arbitrary code execution or memory corruption. The patch does not prove consensus safety failure or ledger/state corruption. The patch does not show a cryptographic break or replay bypass. The core/src/crds_gossip_pull.rs visibility changes are not independently proven to fix a security bug. The evidence supports validator panic/availability impact from malformed network input, not broader protocol compromise. Confirmed by commit message and direct code change in Bloom<T>::sanitize. No evidence supports arbitrary code execution, memory corruption, ledger corruption, cryptographic break, replay bypass, or consensus safety failure. Helper visibility and test-only changes should be treated as adjacent cleanup unless further evidence proves otherwise. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `panic-dos`
Final impact type: `availability`
Final tags: `blockchain-core, gossip, input-validation, bloom-filter, panic, denial-of-service, network-input`

The supplied evidence supports keeping this as a security fix, but the original storage/state-corruption framing is misleading. The commit message explicitly states that pull requests received over the wire can cause a validator panic due to division by zero in bloom filters, and the patch adds Bloom<T>::sanitize validation to reject empty bit vectors before self.pos(...) can divide by zero. The supported impact is remote availability denial of service against a validator, not state integrity, storage corruption, signature, replay, or snapshot compromise.

## Security Evidence

1. Commit body says over-the-wire pull requests can cause a validator panic through division by zero in bloom filters.
2. runtime/src/bloom.rs changed Bloom<T> sanitization from an empty implementation to explicit validation.
3. The new sanitize method rejects self.bits.is_empty() with SanitizeError::InvalidValue.
4. The added code comment directly ties the check to avoiding division by zero in self.pos(...).
5. Changed files include CRDS gossip pull code, consistent with the stated network pull request path.

## Missing Evidence

1. No evidence of ledger/state corruption or state-integrity impact.
2. No evidence of arbitrary code execution, memory corruption, or privilege escalation.
3. No evidence of cryptographic, signature, replay, snapshot, or queue-specific vulnerability.
4. The CRDS helper visibility changes are not independently proven to fix a security issue.

## Claim Boundaries

1. Classify as malformed network input causing validator panic/availability denial of service.
2. Do not claim consensus safety failure or state corruption from the supplied patch alone.
3. Do not treat adjacent CRDS helper cleanup as a separate security fix.
4. Security relevance depends on the commit message plus direct sanitization patch; the code alone mainly shows invariant hardening against division by zero.
