# Validation Card

## Metadata

- ID: `stacks-core-2023-11-14-stacks-core-storage-3ae5e37f0e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-signature-type-hardening`

## What Confirmed The Issue

- Evidence 1: In `stackslib/src/chainstate/nakamoto/mod.rs`, the patch replaces `if !sortdb.expects_stacker_signature(` with `let schnorr_signature = block.header.stacker_signature.to_wsts_signature().ok_or({`.
- Evidence 2: In `stackslib/src/chainstate/burn/db/sortdb.rs`, the patch replaces `_stacker_signature: &MessageSignature,` with `_stacker_signature: &WSTSSignature,`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
