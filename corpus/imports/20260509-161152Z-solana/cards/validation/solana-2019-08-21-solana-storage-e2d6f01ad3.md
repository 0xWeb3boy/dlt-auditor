# Validation Card

## Metadata

- ID: `solana-2019-08-21-solana-storage-e2d6f01ad3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-genesis-blockhash-validation`

## What Confirmed The Issue

- Adds expected_genesis_blockhash to validator configuration and propagates it during entrypoint-based startup.
- Computes GenesisBlock::load(...).hash() and compares it against the expected cluster genesis blockhash.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
