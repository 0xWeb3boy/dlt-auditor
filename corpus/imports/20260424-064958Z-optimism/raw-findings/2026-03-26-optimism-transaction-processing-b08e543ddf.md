---
case_id: case_20260326_b08e543ddf
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-26
source_refs:
  - git:b08e543ddfb2c49be51a351c10135bdedcb8152d
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:69"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:54"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:186"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:110"
bug_class: resource-exhaustion
impact_type:
  - denial-of-service
confidence: medium
tags:
  - decompression
  - resource-limits
  - protocol-parsing
  - blockchain-core
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a correctness fix in batch/channel decompression: Brotli output handling was changed from reject-on-growth-limit behavior to capped truncation behavior, and the batch reader now makes repeated decompression calls explicit. That is protocol- and robustness-relevant, but the supplied code excerpts do not by themselves establish a proven security vulnerability.

## Observed Patch Facts

1. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch replaces `if let Some(data) = self.data.take() {` with `/// No-op if the data has already been decompressed.`.

2. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch replaces `),` with `);`.

3. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch adds `/// Builds zlib-compressed channel data containing 'n' copies of the same`.

4. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `rust/kona/crates/protocol/protocol/src/batch`, `rust/kona/crates/protocol/protocol/src`, `rust/kona/crates/protocol/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs`. The strongest project-level identifiers around this patch are `data`, `DecompressionError::EmptyData`, `decompressed`, and `DecompressionError`.

## Before/After Behavior

Before the patch, the Brotli path used a growth loop that could return `BatchTooLarge` when the next buffer expansion would exceed `max_rlp_bytes_per_channel`, and `BatchReader::decompress` did not have an explicit early-success path for already decompressed data. After the patch, `BatchReader::decompress` returns success when output is already present, explicitly errors on missing or empty source data, and the Brotli path treats output-at-cap as a stop/truncation condition instead of immediate rejection.

# Root Cause

The decompression boundary did not encode the size-cap behavior explicitly enough: limit handling in the Brotli path was tied to buffer growth/rejection behavior rather than a clear capped-output rule, and reader state handling around already-decompressed data was implicit.

## Walkthrough

1. The evidence places the change in the protocol batch-processing path used for L2 derivation.

2. `BatchReader::decompress` now first checks whether `self.decompressed` is already populated and returns `Ok(())` in that case.

3. The same function now distinguishes `None`, empty input, and real input explicitly when consuming `self.data`.

4. The Brotli routine previously centered on `NeedsMoreOutput` and buffer growth, with rejection once a further growth step would exceed the configured limit.

5. The revised Brotli code uses a limit-capped output buffer and comments indicate that once the buffer is full at the cap, decoding stops per spec instead of rejecting.

6. New tests cover truncation behavior and additional decompression-path handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 69 | batch reader decompression entrypoint and decompressed-state handling for channel data |
| rust/kona/crates/protocol/protocol/src/brotli.rs | 19 | bounded Brotli decompression routine enforcing channel output cap and truncation semantics |

## Code Snippets

## Snippet 1

Context: `rust/kona/crates/protocol/protocol/src/batch/reader.rs:69` (changes a sensitive control or state-update path)

Before
```rust
/// Helper method to decompress the data contained in the reader.
    pub fn decompress(&mut self) -> Result<(), DecompressionError> {
        if let Some(data) = self.data.take() {
            // Peek at the data to determine the compression type.
            if data.is_empty() {
                return Err(DecompressionError::EmptyData);
            }
```
After
```rust
/// Helper method to decompress the data contained in the reader.
    /// No-op if the data has already been decompressed.
    pub fn decompress(&mut self) -> Result<(), DecompressionError> {
        if !self.decompressed.is_empty() {
            return Ok(());
        }
        match self.data.take() {
```

## Snippet 2

Context: `rust/kona/crates/protocol/protocol/src/brotli.rs:54` (changes a sensitive control or state-update path)

Before
```rust
&mut written,
            &mut brotli_state,
        ),
        brotli::BrotliResult::NeedsMoreOutput
    ) {
        // Resize the output buffer to double the size, following standard
        // practice for buffer resizing in streams.
        let old_len = output.len();
```
After
```rust
&mut written,
            &mut brotli_state,
        );
        let old_len = output.len();

        match result {
            // Buffer was already grown to the limit on a previous iteration, but the decompressor
            // filled it and still has more to produce: stop per spec.
```

## Snippet 3

Context: `rust/kona/crates/protocol/protocol/src/batch/reader.rs:186` (changes bounds, limits, or capacity handling)

Before
```rust
assert_eq!(reader.cursor, decompressed_len);
    }
}
```
After
```rust
assert_eq!(reader.cursor, decompressed_len);
    }

    /// Builds zlib-compressed channel data containing `n` copies of the same
    /// batch by duplicating the decompressed RLP content from the test fixture.
    fn new_multi_batch_compressed_data(n: usize) -> (Bytes, usize) {
        let raw = new_compressed_batch_data();
        let single = decompress_to_vec_zlib(&raw).unwrap();
```

## Snippet 4

Context: `rust/kona/crates/protocol/protocol/src/brotli.rs:110` (changes bounds, limits, or capacity handling)

Before
```rust
assert_eq!(decompressed, raw_batch_decompressed);
    }
}
```
After
```rust
assert_eq!(decompressed, raw_batch_decompressed);
    }

    #[test]
    fn test_brotli_truncation_instead_of_rejection() {
        // Use the small test data to verify truncation behavior.
        let expected = hex!("75ed184249e9bc19675e");
        let compressed = hex!("8b048075ed184249e9bc19675e03");
```

# Fix Pattern

Make boundary handling explicit: cap decompression output, stop at the configured limit instead of overgrowing or rejecting on the next resize step, and make reader decompression state idempotent.

## How It Was Fixed

The patch changes the reader entrypoint so repeated decompression is a no-op success and absent or empty input is handled explicitly. It also changes Brotli decompression so output growth is bounded by `max_rlp_bytes_per_channel` and limit hits are handled as truncation/stop behavior, with regression tests added for that case.

# Why It Matters

1. It makes decompression behavior deterministic at the configured size cap.

2. It reduces divergence between implementation behavior and the stated truncation rule.

3. It improves robustness when decompression is invoked more than once.

4. The supplied evidence does not prove more than correctness and hardening effects.

# Evidence Notes

Direct support comes from the shown changes in `rust/kona/crates/protocol/protocol/src/batch/reader.rs` and `rust/kona/crates/protocol/protocol/src/brotli.rs`, plus tests added in those files. The commit message mentions stronger claims such as zip-bomb OOM prevention and zlib changes, but those specific implementation changes are not visible in the provided code excerpts, so they should not be treated as fully validated here. Protocol security invariant: Compressed channel data should be decompressed with a clear byte cap and deterministic handling at that cap so batch parsing does not diverge on oversized or repeated inputs. Verification notes: The provided diff evidence directly supports the channel decompression changes, not the full trace-extension and TipCursor fixes mentioned in the commit body. The patch shows resource bounding and spec alignment, but does not by itself prove practical exploitability in deployed dispute games. No evidence here proves code execution, privilege escalation, or a chain-wide consensus split from this decompression bug alone. The Brotli truncation behavior is directly supported by the added test in `brotli.rs`. The repeated-decompression no-op behavior is directly supported by the new early return in `BatchReader::decompress`. No supplied excerpt directly shows the claimed zlib bounding change. No supplied excerpt proves exploitability beyond protocol/correctness and robustness concerns. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `decompression, resource-limits, protocol-parsing, blockchain-core`

The supplied patch evidence is strong enough to keep this as a security-hardening case. The changed Brotli decompression path now caps allocation/growth at `max_rlp_bytes_per_channel`, explicitly stops at the limit, and adds regression coverage for truncation-at-cap behavior in a batch/channel parsing path that consumes externally supplied compressed data. That is a clear reduction of denial-of-service risk from oversized compressed inputs. The excerpts do not prove a concrete exploitable vulnerability or validate the broader commit-message claims about zlib OOM, so this should not be elevated to a confirmed security-fix.

## Security Evidence

1. Brotli decompression now caps the initial output buffer at `max_rlp_bytes_per_channel` to avoid over-allocation.
2. The decompression loop is changed to stop at the configured cap instead of continuing growth past the limit.
3. New tests explicitly validate truncation-at-limit behavior rather than rejection, showing deliberate resource-bound enforcement.
4. The affected code is in batch/channel derivation logic that processes compressed protocol input, making the resource bound security-relevant.

## Missing Evidence

1. No supplied diff excerpt shows the claimed zlib limit change or the exact pre-patch unbounded zlib call.
2. No evidence demonstrates an actual crash, OOM, or remotely triggerable exploit in deployed nodes.
3. The excerpts do not show attack reachability, privileges required, or real-world impact beyond hardening/resource control.

## Claim Boundaries

1. Supported claim: the patch hardens decompression resource handling for compressed channel/batch input.
2. Supported claim: the change reduces denial-of-service risk from oversized compressed data.
3. Not supported from the excerpts alone: a proven exploitable security bug was fixed.
4. Not supported from the excerpts alone: the full commit-body claims about all affected subsystems, including zlib and dispute-game outcomes.
