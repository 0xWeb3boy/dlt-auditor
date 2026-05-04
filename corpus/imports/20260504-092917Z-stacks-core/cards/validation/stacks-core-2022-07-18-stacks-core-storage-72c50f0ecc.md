# Validation Card

## Metadata

- ID: `stacks-core-2022-07-18-stacks-core-storage-72c50f0ecc`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-binding`

## What Confirmed The Issue

- Evidence 1: In `src/net/rpc.rs`, the patch replaces `let response = match proposal.validate(chainstate, &sortdb.index_conn()) {` with `let signing_contract = match signing_contract {`.
- Evidence 2: In `testnet/stacks-node/src/config.rs`, the patch replaces `None => HELIUM_DEFAULT_CONNECTION_OPTIONS.clone(),` with `};`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
