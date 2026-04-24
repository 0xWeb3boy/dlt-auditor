# Validation Card

## Metadata

- ID: `bor-2026-02-17-bor-cryptography-d9fac7a4c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Clique and Bor replace Uint64()-based continuity checks with exact big.Int arithmetic in header validation.
- The new consensus checks distinguish malformed block numbering from unknown ancestry, tightening validation of untrusted headers.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: hardening
- Expected severity band: low

## False-Positive Cautions

- No proof that the prior Uint64() logic was exploitable in practice or caused consensus acceptance of invalid blocks.
- No evidence of a demonstrated attacker-controlled exploit, consensus split, signature forgery, or remotely triggerable DoS.
