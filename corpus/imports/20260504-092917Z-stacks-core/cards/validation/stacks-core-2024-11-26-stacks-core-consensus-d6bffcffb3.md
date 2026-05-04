# Validation Card

## Metadata

- ID: `stacks-core-2024-11-26-stacks-core-consensus-d6bffcffb3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-state-validation`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/client/stacks_client.rs`, the patch replaces `/// Submit the block proposal to the stacks node. The block will be validated and ret [truncated]` with `#[cfg(any(test, feature = "testing"))]`.
- Evidence 2: In `stacks-signer/src/signerdb.rs`, the patch replaces `/// Return the last accepted block in a tenure (identified by its consensus hash).` with `/// Return the last accepted block the signer (highest stacks height). It will tie br [truncated]`.

## What Could Have Invalidated It

- Compensating control 1: The stale value may be advisory and rechecked before commit.
- Compensating control 2: Single-node local caches may be invalidated by broader lifecycle hooks not visible in the hunk.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: The stale value may be advisory and rechecked before commit.
- Caution 2: Single-node local caches may be invalidated by broader lifecycle hooks not visible in the hunk.
