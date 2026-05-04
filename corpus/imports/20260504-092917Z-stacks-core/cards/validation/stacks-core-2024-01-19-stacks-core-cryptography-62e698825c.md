# Validation Card

## Metadata

- ID: `stacks-core-2024-01-19-stacks-core-cryptography-62e698825c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-request-validation-hardening`

## What Confirmed The Issue

- Evidence 1: In `stacks-signer/src/runloop.rs`, the patch replaces `// A coordinator could have sent a signature share request with a different message t [truncated]` with `if !self.validate_signature_share_request(request) {`.
- Evidence 2: In `stacks-signer/src/runloop.rs`, the patch replaces `/// Helper function to verify a chunk is a valid wsts packet.` with `/// Helper function to validate a signature share request, updating its message where [truncated]`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
