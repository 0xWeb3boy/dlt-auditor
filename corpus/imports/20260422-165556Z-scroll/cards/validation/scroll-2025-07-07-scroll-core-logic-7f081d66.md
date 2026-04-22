# Validation Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-7f081d66`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: In `crates/libzkp/src/lib.rs`, the patch replaces `let task = serde_json::from_str::<ChunkProvingTask>(task_json)?;` with `let mut task = serde_json::from_str::<ChunkProvingTask>(task_json)?;`.
- Evidence 2: In `crates/libzkp/src/lib.rs`, the patch replaces `fork_name: &str,` with `fork_name_str: &str,`.
- Evidence 3: In `crates/libzkp/src/lib.rs`, the patch changes a sensitive implementation path.

## What Could Have Invalidated It

- Compensating control 1: If the duplicated field is never attacker-controlled or never diverges semantically, a similar cleanup may be lower value.
- Compensating control 2: The important signal is not string normalization alone, but the added rejection of mismatched fork identity before task construction.
- Compensating control 3: The evidence supports consistency hardening, not a demonstrated acceptance of malformed proofs.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the duplicated field is never attacker-controlled or never diverges semantically, a similar cleanup may be lower value.
- Caution 2: The important signal is not string normalization alone, but the added rejection of mismatched fork identity before task construction.
- Caution 3: The evidence supports consistency hardening, not a demonstrated acceptance of malformed proofs.
