---
case_id: case_20260413_e2253914e7
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: medium
date: 2026-04-13
source_refs:
  - git:e2253914e7b7eaa7559916809e08c947fe493a21
  - "rust/kona/crates/protocol/derive/src/stages/channel/channel_reader.rs:69"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:55"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:137"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:41"
bug_class: untrusted-input-in-protocol-activation-check
impact_type:
  - consensus-deviation
confidence: medium
tags:
  - blockchain-core
  - consensus
  - hardfork-activation
  - untrusted-input
  - compression
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

`BatchReader` used the decoded batch timestamp to decide whether brotli was allowed under Fjord, even though the derivation pipeline already had the L1 origin timestamp. The patch passes `origin.timestamp` into `BatchReader` and uses that trusted value for the Fjord check, matching the commit's stated goal of preventing a malicious batcher from causing kona and op-node to diverge on channel acceptance.

## Observed Patch Facts

1. In `rust/kona/crates/protocol/derive/src/stages/channel/channel_reader.rs`, the patch replaces `self.next_batch =` with `self.next_batch = Some(BatchReader::new(`.

2. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch replaces `/// Creates a new ['BatchReader'] from the given data and max decompressed RLP bytes per` with `/// Creates a new ['BatchReader'] from the given data, max decompressed RLP bytes per`.

3. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch replaces `// Confirm that brotli decompression was performed *after* the Fjord hardfork.` with `// Accept brotli only after Fjord activation (per L1 origin timestamp).`.

4. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch adds `/// The L1 origin block timestamp, used for hardfork activation checks.`.

## Project Context

The changed code sits primarily in `rust/kona/crates/protocol/derive/src/stages/channel`, `rust/kona/crates/protocol/derive/src/stages`, `rust/kona/crates/protocol/protocol/src/batch`, which anchors the finding in the `consensus` area of the project. Historical context from `rust/kona/crates/protocol/derive/src/stages/channel/channel_assembler.rs`, `rust/kona/crates/protocol/derive/src/stages/channel/channel_provider.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/kona/crates/protocol/derive/src/stages/batch/batch_queue.rs`, `rust/kona/crates/protocol/derive/src/stages/channel/channel_assembler.rs`. The strongest project-level identifiers around this patch are `BatchReader::new`, `timestamp`, `BatchReader`, and `channel`.

## Before/After Behavior

Before the patch, `BatchReader::next_batch` rejected brotli when `cfg.is_fjord_active(batch.timestamp())` was false, so the decision depended on the decoded batch timestamp. After the patch, `channel_reader` passes `origin.timestamp` into `BatchReader`, the reader stores it, and the brotli gate uses `cfg.is_fjord_active(self.origin_timestamp)` instead.

# Root Cause

A hardfork-activation decision in the batch reader trusted `batch.timestamp()` from decoded batch data instead of the L1 origin timestamp already available in the derivation pipeline.

## Walkthrough

1. `channel_reader.rs` already fetched `origin` and used `origin.timestamp` to choose the per-channel RLP limit, but previously did not pass that timestamp into `BatchReader::new`.

2. `BatchReader::new` in `reader.rs` was extended to take `origin_timestamp: u64`, and `BatchReader` gained an `origin_timestamp` field documented for hardfork activation checks.

3. In `BatchReader::next_batch`, the brotli gate changed from `!cfg.is_fjord_active(batch.timestamp())` to `!cfg.is_fjord_active(self.origin_timestamp)`.

4. The commit body states the old behavior let a malicious batcher place a pre-Fjord batch timestamp inside a post-Fjord brotli channel, making kona reject the channel while op-node accepted it.

5. The fix makes this check depend on trusted derivation context, restoring implementation agreement for this brotli/Fjord decision path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/kona/crates/protocol/derive/src/stages/channel/channel_reader.rs | 59 | Derivation stage wires the trusted L1 origin timestamp into `BatchReader` construction for each channel. |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 35 | `BatchReader` state now carries the trusted origin timestamp used for protocol activation checks. |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 128 | Batch acceptance path now checks Fjord brotli eligibility against `self.origin_timestamp` instead of the untrusted decoded batch timestamp. |

## Code Snippets

## Snippet 1

Context: `rust/kona/crates/protocol/derive/src/stages/channel/channel_reader.rs:69` (changes a sensitive control or state-update path)

Before
```rust
};

            self.next_batch =
                Some(BatchReader::new(&channel[..], max_rlp_bytes_per_channel as usize));
            kona_macros::set!(gauge, crate::metrics::Metrics::PIPELINE_BATCH_READER_SET, 1);
        }
```
After
```rust
};

            self.next_batch = Some(BatchReader::new(
                &channel[..],
                max_rlp_bytes_per_channel as usize,
                origin.timestamp,
            ));
            kona_macros::set!(gauge, crate::metrics::Metrics::PIPELINE_BATCH_READER_SET, 1);
```

## Snippet 2

Context: `rust/kona/crates/protocol/protocol/src/batch/reader.rs:55` (changes a sensitive control or state-update path)

Before
```rust
pub const CHANNEL_VERSION_BROTLI: u8 = 1;

    /// Creates a new [`BatchReader`] from the given data and max decompressed RLP bytes per
    /// channel.
    pub fn new<T>(data: T, max_rlp_bytes_per_channel: usize) -> Self
    where
        T: Into<Vec<u8>>,
```
After
```rust
pub const CHANNEL_VERSION_BROTLI: u8 = 1;

    /// Creates a new [`BatchReader`] from the given data, max decompressed RLP bytes per
    /// channel, and the L1 origin block timestamp (used for hardfork activation checks).
    pub fn new<T>(data: T, max_rlp_bytes_per_channel: usize, origin_timestamp: u64) -> Self
    where
        T: Into<Vec<u8>>,
```

## Snippet 3

Context: `rust/kona/crates/protocol/protocol/src/batch/reader.rs:137` (changes a sensitive control or state-update path)

Before
```rust
};

        // Confirm that brotli decompression was performed *after* the Fjord hardfork.
        if self.brotli_used && !cfg.is_fjord_active(batch.timestamp()) {
            return None;
        }
```
After
```rust
};

        // Accept brotli only after Fjord activation (per L1 origin timestamp).
        if self.brotli_used && !cfg.is_fjord_active(self.origin_timestamp) {
            return None;
        }
```

## Snippet 4

Context: `rust/kona/crates/protocol/protocol/src/batch/reader.rs:41` (changes a sensitive control or state-update path)

Before
```rust
/// Whether brotli decompression was used.
    pub brotli_used: bool,
}
```
After
```rust
/// Whether brotli decompression was used.
    pub brotli_used: bool,
    /// The L1 origin block timestamp, used for hardfork activation checks.
    pub origin_timestamp: u64,
}
```

# Fix Pattern

Propagate trusted protocol context into lower-level parsing logic and use it for feature-activation checks instead of attacker-influenced payload fields.

## How It Was Fixed

The derivation stage now constructs `BatchReader` with `origin.timestamp`. `BatchReader` stores that value and uses it for the Fjord brotli activation check, replacing the prior use of the decoded batch timestamp.

# Why It Matters

1. Stops a payload-derived timestamp from controlling a hardfork-gated acceptance rule.

2. Addresses the specific divergence described in the commit body: kona reject vs op-node accept.

3. Keeps brotli/Fjord activation decisions tied to trusted L1 origin context.

# Evidence Notes

Direct code evidence shows `origin.timestamp` added to `BatchReader::new`, stored on `BatchReader`, and substituted for `batch.timestamp()` in the brotli/Fjord gate. The commit body explicitly describes the prior input as an untrusted batch timestamp and states a malicious batcher could trigger a consensus deviation between kona and op-node. The supplied evidence supports this specific brotli/Fjord mismatch; it does not establish broader parser flaws or other affected gates. Protocol security invariant: The Fjord hardfork gate for brotli-compressed channel data must be evaluated from trusted L1 origin context, not from batch payload timestamps. Nodes given the same origin must make the same accept/reject decision for brotli channels. Verification notes: The patch proves a consensus-rule mismatch, not remote code execution or memory corruption. The evidence shows a malicious batcher can trigger divergent accept/reject behavior, but does not quantify chain impact beyond consensus deviation. The patch does not show that other hardfork checks or other compression paths were affected. The evidence is specific to kona previously disagreeing with op-node on this brotli/Fjord gate; it does not show a broader protocol design flaw. No test changes were provided in the supplied evidence. The security conclusion relies on both the code diff and the commit body's explicit failure-mode description. The evidence is sufficient for this specific brotli activation bug, but not for claims about other hardfork checks or compression paths. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `untrusted-input-in-protocol-activation-check`
Final impact type: `consensus-deviation`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, hardfork-activation, untrusted-input, compression`

The supplied evidence supports a real security-relevant fix in a consensus-critical path. Before the patch, brotli eligibility under the Fjord fork was decided from `batch.timestamp()`, which the commit body describes as attacker-controlled batch data. The patch replaces that with the trusted L1 origin timestamp already available in the derivation pipeline. In a blockchain client, a maliciously triggerable accept/reject mismatch against another implementation is a concrete security issue, not just reliability or cleanup. The exact downstream impact is not fully proven from the diff alone, so the retained classification should stay conservative on confidence and impact scope.

## Security Evidence

1. The patch changes the Fjord activation check from `cfg.is_fjord_active(batch.timestamp())` to `cfg.is_fjord_active(self.origin_timestamp)`.
2. `BatchReader` now stores `origin_timestamp`, indicating the gate should use trusted derivation context rather than decoded batch contents.
3. `channel_reader` passes `origin.timestamp` into `BatchReader::new`, showing the fix propagates trusted L1 state into the validation path.
4. The commit message explicitly states a malicious batcher could craft input that made kona reject a channel while op-node accepted it, causing consensus deviation.

## Missing Evidence

1. No test diff is shown demonstrating the divergence before the fix or agreement after the fix.
2. The patch does not quantify whether the mismatch could cause chain split, node desync, or only local derivation failure.
3. The evidence does not show whether similar activation checks elsewhere had the same trust-boundary mistake.

## Claim Boundaries

1. The evidence supports this specific brotli/Fjord activation bug in `BatchReader`, not a broader parser or compression vulnerability.
2. The evidence supports consensus deviation risk between implementations; it does not prove remote code execution, memory corruption, or key compromise.
3. The evidence supports attacker influence via crafted batch data, but not the full operational severity on a live network.
