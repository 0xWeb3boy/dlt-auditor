# Validation Card

## Metadata

- ID: `stacks-core-2024-02-14-stacks-core-transaction-processing-5ad797514e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-message-validation`

## What Confirmed The Issue

- Evidence 1: In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces `// Get the block slot for every signer` with `// Get the slots for every signer`.
- Evidence 2: In `testnet/stacks-node/src/nakamoto_node/miner.rs`, the patch replaces an explicit unimplemented validation placeholder with `for transaction in transactions {`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
