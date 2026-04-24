# Validation Card

## Metadata

- ID: `bor-2025-11-28-bor-cryptography-544e6b7c7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-truncation`

## What Confirmed The Issue

- verifySeal previously compared header.Difficulty.Uint64() directly, which would truncate high bits above 64 bits.
- The patch adds header.Difficulty == nil || !header.Difficulty.IsUint64() rejection in the seal-verification path before comparing expected difficulty.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No proof that the pre-patch behavior was exploitable in practice on a live network.
- No evidence of an actual consensus split, validator bypass, or unauthorized block acceptance beyond malformed-width handling.
