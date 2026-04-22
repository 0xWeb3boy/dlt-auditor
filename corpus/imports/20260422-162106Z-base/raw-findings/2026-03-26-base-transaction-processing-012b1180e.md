---
case_id: case_20260326_012b1180e
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2026-03-26
source_refs:
  - git:012b1180e727e7481f1d131e31d64cf111be61cd
  - "crates/consensus/protocol/src/batch/reader.rs:71"
  - "crates/proof/client/src/prologue.rs:84"
  - "crates/proof/client/src/prologue.rs:57"
  - "crates/consensus/protocol/src/batch/reader.rs:189"
bug_class: proof-claim-validation
impact_type:
  - denial-of-service
tags:
  - blockchain-core
  - proof-validation
  - consensus
  - denial-of-service
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The strongest supported security-relevant change is in the proof client: pre-patch logic treated output-root equality as a trace-extension signal before checking the claim against safe-head height. The patch instead fetches the safe head, rejects claims below that height, and adds an explicit safe-head zero-step case that only accepts the agreed output root. The commit message also describes decompression OOM hardening, but the provided code excerpts do not fully prove that part.

## Observed Patch Facts

1. In `crates/consensus/protocol/src/batch/reader.rs`, the patch replaces `if let Some(data) = self.data.take() {` with `/// No-op if the data has already been decompressed.`.

2. In `crates/proof/client/src/prologue.rs`, the patch replaces `let cursor = new_oracle_pipeline_cursor(` with `// If the claim targets the safe head block itself, no derivation is needed. This is the`.

3. In `crates/proof/client/src/prologue.rs`, the patch replaces `if boot.agreed_l2_output_root == boot.claimed_l2_output_root {` with `fetch_safe_head_hash(oracle.as_ref(), boot.agreed_l2_output_root).await?;`.

4. In `crates/consensus/protocol/src/batch/reader.rs`, the patch adds `/// Builds zlib-compressed channel data containing 'n' copies of the same`.

## Project Context

The changed code sits primarily in `crates/consensus/protocol/src/batch`, `crates/consensus/protocol/src`, `crates/proof/client/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/proof/client/src/driver.rs`, `crates/consensus/protocol/src/batch/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/protocol/src/lib.rs`, `crates/proof/client/src/driver.rs`. The strongest project-level identifiers around this patch are `data`, `boot`, `DecompressionError::EmptyData`, and `root`.

## Before/After Behavior

Before the patch, the proof path could classify a case as trace extension based only on agreed-output-root and claimed-output-root equality, before performing safe-head-based height checks. After the patch, the code fetches the safe head from the agreed output root, rejects claims whose claimed L2 block number is below the safe head, and treats the equal-height case as a zero-step transition where the claimed output root must exactly match the agreed output root. Separately, the provided batch-reader excerpt shows decompression becoming a no-op when already decompressed and handling None and empty input explicitly, but it does not by itself demonstrate the full truncation-based OOM fix described in the commit body.

# Root Cause

The proof client relied on a weaker proxy invariant, output-root equality, instead of validating the claim against the canonical protocol state: the claimed L2 block number relative to the safe head.

## Walkthrough

1. The pre-patch proof code returned TraceExtension when agreed_l2_output_root equaled claimed_l2_output_root, so the decision was made from root equality alone.

2. The patched code removes that early equality-based shortcut and first fetches the safe head using the agreed output root.

3. It then resolves the safe head header and rejects claims whose claimed_l2_block_number is less than safe_head.number.

4. It adds a dedicated equal-height branch for claimed_l2_block_number == safe_head.number and requires claimed_l2_output_root to equal agreed_l2_output_root in that zero-step case.

5. That change ties trace-extension handling to block height and safe-head state rather than to reused output roots alone.

6. The batch-reader snippet shows more explicit decompression state handling, but the supplied excerpts do not directly show the zlib or brotli truncation logic mentioned in the commit body.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/proof/client/src/prologue.rs | 47 | Boot-time validation of claimed L2 block number and agreed safe-head anchor before proof derivation proceeds |
| crates/proof/client/src/prologue.rs | 84 | Trace-extension leaf handling for the zero-step case, requiring the claimed output root to equal the agreed safe-head output root |
| crates/consensus/protocol/src/batch/reader.rs | 59 | Batch decompression entrypoint that now preserves one-shot semantics and participates in bounded decoding of untrusted compressed channel data |
| crates/consensus/protocol/src/brotli.rs | 8 | Brotli decompression implementation used by batch decoding, relevant to enforcing output truncation instead of unbounded growth |

## Code Snippets

## Snippet 1

Context: `crates/consensus/protocol/src/batch/reader.rs:71` (changes a sensitive control or state-update path)

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

Context: `crates/proof/client/src/prologue.rs:84` (changes a sensitive control or state-update path)

Before
```rust
}

        let cursor = new_oracle_pipeline_cursor(
            rollup_config.as_ref(),
            safe_head,
            &mut l1_provider,
            &mut l2_provider,
```
After
```rust
}

        // If the claim targets the safe head block itself, no derivation is needed. This is the
        // trace-extension leaf case where the trace is capped at the root-claim block number.
        // The only valid output root here is the agreed output root (a zero-step transition).
        if boot.claimed_l2_block_number == safe_head.number {
            if boot.claimed_l2_output_root != boot.agreed_l2_output_root {
                error!(
```

## Snippet 3

Context: `crates/proof/client/src/prologue.rs:57` (changes a sensitive control or state-update path)

Before
```rust
let rollup_config = Arc::new(boot.rollup_config);

        if boot.agreed_l2_output_root == boot.claimed_l2_output_root {
            info!("trace extension detected");
            return Err(FaultProofProgramError::TraceExtension);
        }

        let safe_head_hash =
```
After
```rust
let rollup_config = Arc::new(boot.rollup_config);

        let safe_head_hash =
            fetch_safe_head_hash(oracle.as_ref(), boot.agreed_l2_output_root).await?;
```

## Snippet 4

Context: `crates/consensus/protocol/src/batch/reader.rs:189` (changes bounds, limits, or capacity handling)

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

# Fix Pattern

Replace indirect equality-based detection with explicit validation against protocol state, and add a dedicated zero-step rule for the safe-head case.

## How It Was Fixed

The fix removed the early output-root-equality TraceExtension check, fetched the safe head from the agreed output root, rejected claims below safe-head height, and added an explicit safe-head leaf case that only accepts the agreed output root. The commit message further states that decompression output was bounded, but that portion is only partially evidenced in the provided snippets.

# Why It Matters

1. It prevents proof-path decisions from depending only on a reused output root.

2. It binds claim validation to the claimed block height and the agreed safe-head anchor.

3. It closes an ambiguity around the zero-step safe-head case.

4. The decompression hardening may also matter for memory safety, but that part is only partially shown here.

# Evidence Notes

Direct code evidence is strong for the proof-client change in crates/proof/client/src/prologue.rs: the old early equality check is removed, safe-head lookup is performed first, claims below safe_head.number are rejected, and an equal-height zero-step branch requires the agreed output root. The batch-reader evidence in crates/consensus/protocol/src/batch/reader.rs supports only idempotent decompression entry behavior and explicit None or empty-input handling. The claimed zlib and brotli truncation behavior, the OOM thesis, and the TipCursor initialization change come from the supplied commit body rather than from full implementation hunks in the provided excerpts, so those claims should be treated as partially evidenced only. Protocol security invariant: A disputed L2 claim must be validated against the safe-head block height, and a zero-step claim at the safe head is only valid when its claimed output root equals the agreed output root. Verification notes: The patch does not by itself prove consensus failure or chain takeover; it shows claim-validation and resource-bound enforcement fixes. Exploitability beyond challenge/griefing in the proof path and memory-exhaustion risk in decompression is not demonstrated by the provided diff alone. Not every touched file is independently shown to contain a distinct vulnerability; the commit bundles related correctness and security changes. The evidence does not establish confidentiality impact or arbitrary code execution. Verified from the provided snippets that the early agreed-root-equals-claimed-root TraceExtension check was removed. Verified from the provided snippets that claims below the safe head are rejected and equal-height claims must reuse the agreed output root. Did not directly verify the zlib or brotli truncation implementation from the provided code excerpts. Did not directly verify the TipCursor initialization change from the provided code excerpts. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `proof-claim-validation`
Final impact type: `denial-of-service`
Final tags: `blockchain-core, proof-validation, consensus, denial-of-service`

The supplied patch evidence is strong enough to keep this as a security-fix case, but only for the proof-validation portion of the commit. The before/after in `prologue.rs` shows that the old logic treated output-root equality as a trace-extension signal before validating the claimed block height against the safe head, while the new logic first resolves the safe head, rejects claims below that height, and only allows the zero-step case when the claimed output root matches the agreed output root at the safe head. Combined with the commit body’s explicit attacker scenario, this supports a concrete security-relevant validation flaw that could enable trivial malicious challenges or proof-path disruption. The decompression/OOM claims are not sufficiently proven by the provided excerpts and should not be the basis for validation.

## Security Evidence

1. The commit body explicitly describes a malicious-attacker scenario: anchoring a trace-extension claim at the wrong height while reusing the agreed output root.
2. Pre-patch `prologue.rs` returned `TraceExtension` based on output-root equality alone, without first validating the claimed L2 block number against the safe head.
3. Post-patch `prologue.rs` fetches the safe head from the agreed output root before evaluating the claim.
4. Post-patch logic rejects claims where `claimed_l2_block_number < safe_head.number`, adding an explicit protocol-state validation guard.
5. Post-patch logic adds a dedicated zero-step case for `claimed_l2_block_number == safe_head.number` and requires the claimed output root to equal the agreed output root.

## Missing Evidence

1. The provided excerpts do not show the full surrounding control flow needed to quantify exploit impact beyond proof/challenge disruption.
2. The zlib and brotli truncation changes described in the commit body are not directly shown in the supplied implementation hunks.
3. The TipCursor initialization fix mentioned in the commit body is not directly evidenced in the provided snippets.

## Claim Boundaries

1. Validated as a security fix only for the proof-client claim-validation change in `crates/proof/client/src/prologue.rs`.
2. Do not overclaim confidentiality, code execution, or full consensus compromise from the provided patch alone.
3. The evidence supports proof/challenge-path integrity and availability risk, not a broader transaction-processing vulnerability.
4. The decompression/OOM portion should be treated as unverified from the supplied patch excerpts.
