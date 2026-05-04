# Validation Card

## Metadata

- ID: `stacks-core-2023-01-24-stacks-core-consensus-17ae4d1671`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-unaware-consensus-lookup`

## What Confirmed The Issue

- Evidence 1: In `src/burnchains/db.rs`, the patch replaces `pub fn get_anchor_block_commit(` with `pub fn get_anchor_block_commit_metadatas(`.
- Evidence 2: In `src/burnchains/db.rs`, the patch replaces `pub fn get_heaviest_anchor_block(` with `pub fn get_heaviest_anchor_block<B: BurnchainHeaderReader>(`.

## What Could Have Invalidated It

- Compensating control 1: The value may be used only for display or diagnostics.
- Compensating control 2: Another validation layer may enforce canonical context before finalization.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The value may be used only for display or diagnostics.
- Caution 2: Another validation layer may enforce canonical context before finalization.
