---
case_id: case_20260219_543510ee9b
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: resource-exhaustion
confidence: medium
source_quality: high
date: 2026-02-19
source_refs:
  - git:543510ee9bcd8d1378269c180b40022524fc166b
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:69"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:54"
  - "rust/kona/crates/protocol/protocol/src/batch/reader.rs:186"
  - "rust/kona/crates/protocol/protocol/src/brotli.rs:110"
impact_type:
  - availability
tags:
  - blockchain-core
  - transaction-processing
  - resource-exhaustion
  - decompression
  - availability
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The strongest supported security claim is an availability fix in channel decompression: the commit states the zlib path was changed from unbounded decompression to a limit-aware variant to prevent zip-bomb-style OOM. The same patch also corrects brotli limit handling and partial-output behavior, but those parts are better supported as spec/correctness fixes than as standalone security findings.

## Observed Patch Facts

1. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch replaces `if let Some(data) = self.data.take() {` with `/// No-op if the data has already been decompressed.`.

2. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch replaces `),` with `);`.

3. In `rust/kona/crates/protocol/protocol/src/batch/reader.rs`, the patch adds `/// Builds zlib-compressed channel data containing 'n' copies of the same`.

4. In `rust/kona/crates/protocol/protocol/src/brotli.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `rust/kona/crates/protocol/protocol/src/batch`, `rust/kona/crates/protocol/protocol/src`, `rust/kona/crates/protocol/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/kona/crates/protocol/protocol/src/lib.rs`, `rust/kona/crates/protocol/protocol/src/batch/mod.rs`. The strongest project-level identifiers around this patch are `data`, `DecompressionError::EmptyData`, `decompressed`, and `DecompressionError`.

## Before/After Behavior

Before the patch, the provided brotli hunk doubled the output buffer and returned `BatchTooLarge` if the doubled size would exceed `max_rlp_bytes_per_channel`. The commit body also states the zlib path used unbounded `decompress_to_vec_zlib`. After the patch, the supplied brotli context shows output growth is capped at `max_rlp_bytes_per_channel` and over-limit output is handled by stopping at the cap per spec rather than immediate rejection. `BatchReader::decompress()` also now treats already-populated decompressed state as a no-op and maps missing or empty input to `DecompressionError::EmptyData`. The claim that zlib is now bounded and that partial output is preserved on limit hits or decompression errors comes from the commit body, not a shown code hunk.

# Root Cause

The decompression boundary did not consistently enforce the protocol's output-size limit on untrusted compressed channel data. The clearest security-relevant instance is the zlib path described in the commit body as unbounded, creating OOM risk. Separately, the brotli path handled near-limit expansion with rejection instead of spec-defined truncation.

## Walkthrough

1. `BatchReader` is the entry point for channel decompression before later batch decoding, so decompression behavior affects downstream processing.

2. In `batch/reader.rs`, `decompress()` now returns early if `self.decompressed` is already populated and explicitly maps `None` and empty input to `DecompressionError::EmptyData`.

3. In `brotli.rs`, the supplied context states the initial output buffer is capped and that growth is capped at `max_rlp_bytes_per_channel`.

4. The removed brotli logic rejected when the next doubled buffer would exceed the limit; the new logic handles `NeedsMoreOutput` at the cap by stopping per spec.

5. The commit body explicitly says the zlib path replaced unbounded `decompress_to_vec_zlib` with `decompress_to_vec_zlib_with_limit` to prevent zip-bomb OOM.

6. Added tests exercise larger zlib-derived data and a brotli truncation case, which supports the intended bounded/truncation behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 57 | Batch/channel reader entry point that performs decompression before batch decoding and now treats already-decompressed state and empty input differently. |
| rust/kona/crates/protocol/protocol/src/batch/reader.rs | 69 | Core channel decompression control flow for zlib/brotli inputs; security relevance comes from how partial output and errors are propagated into downstream batch decoding. |
| rust/kona/crates/protocol/protocol/src/brotli.rs | 19 | Brotli decompressor implementation that caps output growth at max_rlp_bytes_per_channel and truncates per spec instead of rejecting or over-growing buffers. |
| rust/kona/crates/protocol/protocol/src/brotli.rs | 54 | Loop handling NeedsMoreOutput / buffer growth during brotli decompression; this is the resource-control boundary for compressed channel input. |

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

Apply decompression-time resource bounds at the codec boundary, and handle over-limit output with explicit protocol behavior instead of decoder-default growth or rejection.

## How It Was Fixed

The patch bounds decompression by the channel size limit. Direct evidence shows the brotli implementation now caps output growth and truncates at the limit per spec. The commit body states the zlib path was switched to a limit-aware decompressor and that partial output is preserved on limit hits or decompression errors.

# Why It Matters

1. Compressed channel data is attacker-controlled input to a critical derivation path.

2. Unbounded decompression can turn small inputs into large memory consumption and cause OOM.

3. Bounding output at the decompression boundary is the relevant availability safeguard.

4. Some other changes in the patch are protocol-correctness fixes, but they accompany the same boundary hardening.

# Evidence Notes

Direct code evidence supports the brotli cap/truncation behavior and the `BatchReader::decompress()` control-flow changes. The specific zlib claim, including the zip-bomb/OOM rationale and the switch to `decompress_to_vec_zlib_with_limit`, is supported by the commit body rather than an extracted diff hunk. The added test helpers are supporting evidence, not the root cause. Protocol security invariant: Untrusted compressed channel data must not be able to expand without a configured per-channel output bound. Decompression should enforce `max_rlp_bytes_per_channel` at the decompression boundary rather than relying on decoder defaults. Verification notes: The patch proves a bounded-vs-unbounded decompression change, but does not by itself prove practical exploitability in deployed nodes. The evidence supports denial-of-service risk from memory growth; it does not show memory corruption, code execution, or privilege escalation. The patch also fixes protocol/spec deviations and false rejections; not every changed hunk is independently a security fix. The provided diff does not prove a live consensus split, only that behavior was inconsistent with spec/reference handling of truncation and partial output. Exact zlib implementation changes are not shown in the supplied snippets. Brotli limit-handling changes are directly visible in the provided code context. The strongest justified security classification is availability/resource exhaustion, not memory corruption or code execution. Brotli truncation and partial-output handling also look like spec/correctness fixes, so the patch is mixed rather than purely security-only. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `availability`
Final tags: `blockchain-core, transaction-processing, resource-exhaustion, decompression, availability`

The supplied evidence is strong enough to keep this as a security-hardening case, not a full security-fix. The patch directly adds and documents decompression output bounds in a channel-processing path for untrusted compressed data, and the commit metadata explicitly frames the zlib change as preventing zip-bomb OOM. That supports a security-focused resource-control hardening classification. However, the extracted diff does not show the zlib call-site change itself or prove a concrete remotely exploitable DoS, so the original `security-fix` and `remote-dos` framing is too strong from the patch alone.

## Security Evidence

1. Commit body explicitly says unbounded zlib decompression was replaced with a limit-aware variant to prevent zip-bomb OOM.
2. `decompress_brotli` now caps the initial output buffer by `max_rlp_bytes_per_channel`.
3. The brotli decompression loop is documented and structured to stop/truncate at the configured limit instead of unbounded growth.
4. The affected code is the channel decompression path before batch decoding, so it handles attacker-influenced compressed input.
5. New tests exercise truncation behavior near the size limit.

## Missing Evidence

1. No direct diff hunk shows the zlib API replacement at the call site.
2. No proof of an observed exploit or demonstrated pre-fix OOM in a deployed node.
3. No evidence here establishes a concrete remote attack path or real-world reachability.
4. Part of the patch is also protocol/spec-correctness work, which dilutes a pure security-fix reading.

## Claim Boundaries

1. This supports decompression-bound enforcement as availability hardening.
2. It does not prove a concrete exploitable remote DoS from the patch alone.
3. It does not support claims of memory corruption, code execution, or privilege escalation.
4. The brotli hardening is directly shown; the zlib OOM rationale depends partly on commit metadata rather than the extracted diff.
