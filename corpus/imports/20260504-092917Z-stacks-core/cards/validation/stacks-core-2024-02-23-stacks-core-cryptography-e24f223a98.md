# Validation Card

## Metadata

- ID: `stacks-core-2024-02-23-stacks-core-cryptography-e24f223a98`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-vote-message-validation`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/signer.rs`, the patch replaces `let block = read_next::<NakamotoBlock, _>(&mut &message[..]).ok().unwrap_or({` with `// We do not sign across blocks, but across their hashes. however, the first sign req [truncated]`.
- Evidence 2: In `stacks-signer/src/signer.rs`, the patch replaces `let message_len = request.message.len();` with `let Some(block_vote): Option<NakamotoBlockVote> = read_next(&mut &request.message[..] [truncated]`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
