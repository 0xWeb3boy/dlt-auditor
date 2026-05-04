# Validation Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-storage-73eb572ac2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-equivocation-detection-gap`

## What Confirmed The Issue

- Evidence 1: In `src/chainstate/stacks/db/blocks.rs`, the patch replaces `// hashes are contiguous enough -- for each seqnum, there is a block with seqnum+1 wi [truncated]` with `// sanity check -- all parent block hashes are unique.
- Evidence 2: In `src/net/mod.rs`, the patch replaces `let mut burndb = self.burndb.take().unwrap();` with `let burndb = self.burndb.take().unwrap();`.

## What Could Have Invalidated It

- Compensating control 1: The value may be used only for display or diagnostics.
- Compensating control 2: Another validation layer may enforce canonical context before finalization.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: The value may be used only for display or diagnostics.
- Caution 2: Another validation layer may enforce canonical context before finalization.
