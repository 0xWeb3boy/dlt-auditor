# Validation Card

## Metadata

- ID: `stacks-core-2024-06-06-stacks-core-storage-a7c5a1f061`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`

## What Confirmed The Issue

- Evidence 1: In `stackslib/src/net/relay.rs`, the patch replaces `Ok(())` with `// is the block signed by the active reward set?`.
- Evidence 2: In `stackslib/src/net/unsolicited.rs`, the patch replaces an explicit unimplemented validation placeholder with `let sn_rc = self`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
