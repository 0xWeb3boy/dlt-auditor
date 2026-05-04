# Validation Card

## Metadata

- ID: `stacks-core-2024-11-22-stacks-core-consensus-848921199d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-validation-race`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/v0/signer.rs`, the patch replaces `if let Err(e) = block_info.mark_locally_accepted(false) {` with `if let Some(block_response) = self.check_block_against_sortition_state(`.
- Evidence 2: In `stacks-signer/src/v0/signer.rs`, the patch replaces `let block_response = if let Some(sortition_state) = sortition_state {` with `let block_response = self.check_block_against_sortition_state(`.

## What Could Have Invalidated It

- Compensating control 1: The stale value may be advisory and rechecked before commit.
- Compensating control 2: Single-node local caches may be invalidated by broader lifecycle hooks not visible in the hunk.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The stale value may be advisory and rechecked before commit.
- Caution 2: Single-node local caches may be invalidated by broader lifecycle hooks not visible in the hunk.
