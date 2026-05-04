# Validation Card

## Metadata

- ID: `stacks-core-2024-01-11-stacks-core-transaction-processing-ff49b79a5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `noncanonical-signing-preimage`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/runloop.rs`, the patch replaces `message: block_validate_ok.block.serialize_to_vec(),` with `let signature_hash = block_validate_ok.block.header.signature_hash().expect("BUG: Sta [truncated]`.
- Evidence 2: In `stacks-signer/src/runloop.rs`, the patch changes a sensitive implementation path.

## What Could Have Invalidated It

- Compensating control 1: The constructor may be used only with trusted constants.
- Compensating control 2: The changed path may improve diagnostics without changing acceptance behavior.

## Severity Guidance

- Expected impact band: `protocol_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The constructor may be used only with trusted constants.
- Caution 2: The changed path may improve diagnostics without changing acceptance behavior.
