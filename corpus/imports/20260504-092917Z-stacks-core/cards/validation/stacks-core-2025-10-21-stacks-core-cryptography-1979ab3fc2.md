# Validation Card

## Metadata

- ID: `stacks-core-2025-10-21-stacks-core-cryptography-1979ab3fc2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ambiguous-crypto-verification-api`

## What Confirmed The Issue

- Evidence 1: In `stacks-common/src/util/secp256r1.rs`, the patch replaces `) -> Result<bool, &'static str> {` with `/// Returns Ok(()) if the signature is valid, or an error otherwise.`.
- Evidence 2: In `stacks-common/src/util/secp256r1.rs`, the patch replaces `let valid = pubk2.verify_digest(&msg_hash, &sig).unwrap();` with `let e = pubk2`.

## What Could Have Invalidated It

- Compensating control 1: A later consensus layer may repeat the full signature check.
- Compensating control 2: The code may only build test fixtures or diagnostics and never trust external messages.

## Severity Guidance

- Expected impact band: `consensus_or_network_integrity`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: A later consensus layer may repeat the full signature check.
- Caution 2: The code may only build test fixtures or diagnostics and never trust external messages.
