# Validation Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## What Confirmed The Issue

- Zero-hash sentinel logic was removed so payload block-hash validation is now unconditional.
- State-root comparison against the block header no longer skips env_switches blocks.

## What Could Have Invalidated It

- No proof that untrusted production inputs could trigger the old bypasses
- No evidence of a demonstrated exploit, consensus split, or accepted malformed block before the patch

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that untrusted production inputs could trigger the old bypasses
- No evidence of a demonstrated exploit, consensus split, or accepted malformed block before the patch
