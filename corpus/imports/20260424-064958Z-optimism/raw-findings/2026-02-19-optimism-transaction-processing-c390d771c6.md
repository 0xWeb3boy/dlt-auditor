---
case_id: case_20260219_c390d771c6
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: resource-exhaustion
confidence: medium
source_quality: high
date: 2026-02-19
source_refs:
  - git:c390d771c65d783503f82fb76fb0b1d8628c605b
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:69"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:54"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:186"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:110"
impact_type:
  - denial-of-service
tags:
  - blockchain-core
  - resource-exhaustion
  - decompression
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

This patch is best supported as an availability fix in the channel decompression path. The provided evidence shows Brotli was changed to honor the per-channel byte limit by truncating at the cap instead of rejecting on a resize threshold, and the commit body explicitly says the zlib path was changed from unbounded decompression to a limit-aware variant to prevent zip-bomb OOM.

## Observed Patch Facts

1. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch replaces `if let Some(data) = self.data.take() {` with `/// No-op if the data has already been decompressed.`.

2. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch replaces `),` with `);`.

3. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch adds `/// Builds zlib-compressed channel data containing 'n' copies of the same`.

4. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `rust/kona/crates/protocol/protocol/src/batch`, `rust/kona/crates/protocol/protocol/src`, `rust/kona/crates/protocol/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs`. The strongest project-level identifiers around this patch are `data`, `DecompressionError::EmptyData`, `decompressed`, and `DecompressionError`.

## Before/After Behavior

Before the patch, the commit body says zlib decompression was unbounded, allowing compressed input to expand until OOM, and the visible Brotli logic rejected some near-limit inputs when the next buffer doubling would exceed max_rlp_bytes_per_channel. After the patch, decompression is performed under the protocol limit, Brotli stops at the cap per spec instead of erroring on that resize condition, and partial in-bounds output is preserved on limit hits or later decompression errors.

# Root Cause

The decompression path did not consistently enforce the protocol's maximum decompressed-size invariant inside the codec operations themselves. That left the zlib path unbounded and made Brotli rely on buffer-growth heuristics that were not equivalent to bounded-prefix handling.

## Walkthrough

1. BatchReader::decompress in rust/kona/crates/protocol/protocol/src/batch/reader.rs is the entry point that consumes stored channel data and fills the decompressed buffer used by later batch decoding.

2. The pre-patch Brotli code in rust/kona/crates/protocol/protocol/src/brotli.rs handled NeedsMoreOutput by doubling the output buffer and returned BatchTooLarge when the next doubling would exceed max_rlp_bytes_per_channel.

3. The patched Brotli code initializes and grows output with the protocol limit as a hard cap and includes comments stating that once the capped buffer is full, processing stops per spec.

4. The commit body explicitly states the zlib path was changed from decompress_to_vec_zlib to decompress_to_vec_zlib_with_limit to prevent zip-bomb OOM.

5. The commit body also states both codecs now preserve partial output on limit hits and decompression errors, and the added tests support the intended truncation behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 69 | BatchReader decompression entry point for channel payloads before batch decoding; dispatches compressed input into bounded decompression and retains partial decoded bytes. |
| rust/kona/crates/protocol/protocol/src/brotli.rs | 19 | Streaming Brotli decompressor for channel data; caps buffer growth at max_rlp_bytes_per_channel and truncates at the protocol limit instead of overgrowing or rejecting. |

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

Apply the protocol size limit inside decompression, cap output-buffer growth at that limit, and preserve the bounded prefix instead of rejecting or expanding without bound.

## How It Was Fixed

The fix bounds decompression by MAX_RLP_BYTES_PER_CHANNEL. Per the commit text, zlib now uses a limit-aware decompressor. In the visible Brotli code, output allocation and growth are capped by max_rlp_bytes_per_channel, and the decoder truncates at the cap per spec rather than treating the next resize as a fatal error. The same change set also preserves already-produced in-bounds bytes on late decompression failures.

# Why It Matters

1. Prevents compressed channel data from causing unbounded memory growth.

2. Addresses the zip-bomb OOM case named in the commit body.

3. Keeps resource usage aligned with the protocol's decompressed-size bound.

4. Avoids dropping valid in-bounds data solely because a later resize or decode step failed.

# Evidence Notes

Direct code evidence is strongest for the Brotli path: the extracted hunk shows the old NeedsMoreOutput resize/error behavior and the new limit-capped truncation logic, with comments explicitly tying it to spec behavior. BatchReader::decompress is shown as the relevant entry point for channel decompression. The zlib OOM claim is supported by the commit body, not by a visible zlib implementation hunk in the provided excerpts. Added tests in reader.rs and brotli.rs support the intended behavioral change but do not by themselves establish exploitability. Protocol security invariant: Channel decompression must enforce MAX_RLP_BYTES_PER_CHANNEL during decoding so compressed input cannot cause unbounded output growth; if the stream exceeds the limit or later errors, only the bounded prefix is treated as channel content. Verification notes: The patch shows denial-of-service style resource control, not memory corruption or code execution. It does not by itself prove which deployed node roles or external actors can feed crafted channels to this path. The same change also fixes protocol/spec compliance and false rejection of valid channels, so not every hunk is purely security-motivated. The patch alone does not prove that prior behavior caused consensus splits in production. The security conclusion is limited to denial-of-service/resource-exhaustion, not memory corruption or code execution. The zlib-specific change is described in the commit body rather than shown directly in the extracted diff hunks. The provided evidence does not establish real-world exploitability details such as attacker reachability or production impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final impact type: `denial-of-service`
Final tags: `blockchain-core, resource-exhaustion, decompression, denial-of-service`

Keep it. The supplied evidence shows a decompression path being changed from unbounded expansion toward explicit per-channel output limits, and the commit body directly states the zlib change was made to prevent zip-bomb OOM. The visible Brotli changes reinforce the same resource-control intent by capping buffer growth and truncating at the protocol limit. That supports a real availability-oriented security fix, although the patch alone does not prove remote attacker reachability, so `remote-dos` is too specific.

## Security Evidence

1. The commit body explicitly says zlib switched from unbounded decompression to a limit-aware API to prevent zip-bomb OOM.
2. The Brotli implementation now caps initial/output buffer growth at `max_rlp_bytes_per_channel` and stops at the limit per spec.
3. The changes sit in the batch/channel decompression path that processes protocol data before batch decoding.
4. The patch adjusts runtime guards and failure handling around decompression size limits rather than only doing cleanup or refactoring.

## Missing Evidence

1. The provided code excerpts do not show the exact zlib call replacement in the source diff.
2. The patch alone does not establish which deployed roles or external actors can feed crafted channels to this path.
3. No exploit demonstration or production impact data is provided beyond the commit description.

## Claim Boundaries

1. This supports a decompression resource-exhaustion and availability fix, not memory corruption or code execution.
2. The evidence does not justify the stronger `remote-dos` claim from patch data alone.
3. Some hunks also address spec compliance and false rejection of valid inputs, so not every line in the commit is purely security-motivated.
