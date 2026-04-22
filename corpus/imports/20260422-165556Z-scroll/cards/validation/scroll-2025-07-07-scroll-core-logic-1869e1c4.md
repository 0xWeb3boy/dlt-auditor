# Validation Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-1869e1c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: In `crates/libzkp/src/lib.rs`, the patch replaces `let task = serde_json::from_str::<ChunkProvingTask>(task_json)?;` with `let mut task = serde_json::from_str::<ChunkProvingTask>(task_json)?;`.
- Evidence 2: In `crates/libzkp/src/lib.rs`, the patch replaces `fork_name: &str,` with `fork_name_str: &str,`.
- Evidence 3: In `crates/libzkp/src/lib.rs`, the patch changes a sensitive implementation path.

## What Could Have Invalidated It

- Compensating control 1: If only one canonical source of fork identity exists at runtime, a similar string-normalization change may be routine hygiene.
- Compensating control 2: String cleanup alone is not enough; the security-relevant part is whether mismatches could reach fork-specific proving logic.
- Compensating control 3: The evidence supports integrity hardening, not a demonstrated verifier bypass.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If only one canonical source of fork identity exists at runtime, a similar string-normalization change may be routine hygiene.
- Caution 2: String cleanup alone is not enough; the security-relevant part is whether mismatches could reach fork-specific proving logic.
- Caution 3: The evidence supports integrity hardening, not a demonstrated verifier bypass.
