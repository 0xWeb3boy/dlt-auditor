# Validation Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-storage-4fd033f283`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-fork-context-reward-set-lookup`

## What Confirmed The Issue

- Evidence 1: In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `let reward_cycle_info = self.get_nakamoto_reward_cycle_info(header.block_height)?;` with `// NOTE(safety): the reason it's safe to use the local best stacks
- Evidence 2: In `stackslib/src/chainstate/nakamoto/coordinator/mod.rs`, the patch replaces `// only proceed if we have processed the _anchor block_ for this reward cycle` with `// NOTE(safety): this is not guaranteed to be the canonical best Stacks

## What Could Have Invalidated It

- Compensating control 1: The value may be used only for display or diagnostics.
- Compensating control 2: Another validation layer may enforce canonical context before finalization.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The value may be used only for display or diagnostics.
- Caution 2: Another validation layer may enforce canonical context before finalization.
