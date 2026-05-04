# Validation Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-consensus-2ecf14d5d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-tip-monotonicity`

## What Confirmed The Issue

- Evidence 1: In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `self.update_canonical_stacks_tip(` with `// arbitrarily.`.
- Evidence 2: In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `/// is the given block a descendant of 'potential_ancestor'?` with `/// Get the block ID of the highest-processed Nakamoto block on this history.`.

## What Could Have Invalidated It

- Compensating control 1: The value may be used only for display or diagnostics.
- Compensating control 2: Another validation layer may enforce canonical context before finalization.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The value may be used only for display or diagnostics.
- Caution 2: Another validation layer may enforce canonical context before finalization.
