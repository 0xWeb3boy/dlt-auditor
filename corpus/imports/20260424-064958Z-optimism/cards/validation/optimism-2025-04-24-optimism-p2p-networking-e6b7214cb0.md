# Validation Card

## Metadata

- ID: `optimism-2025-04-24-optimism-p2p-networking-e6b7214cb0`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `trusted-signer-resolution`

## What Confirmed The Issue

- The commit is explicitly about an "Unsafe Block Signer," a security-sensitive trust input.
- A new unsafe_block_signer(...) helper was added instead of leaving signer resolution implicit.
- The helper consults runtime/L1-backed configuration, suggesting movement toward a more canonical signer source.
- RuntimeLoaderError was added with transport and protocol-version decode variants, supporting fail-closed handling of signer/runtime lookup failures.

## What Could Have Invalidated It

- No excerpt shows the full pre-patch signer source or fallback behavior.
- No excerpt shows the full post-patch unsafe_block_signer implementation.
- No excerpt shows where the resolved signer is enforced in block validation, acceptance, or peer handling.
- No evidence demonstrates a concrete exploit path, consensus break, or arbitrary unsafe block acceptance before the patch.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No excerpt shows the full pre-patch signer source or fallback behavior.
- No excerpt shows the full post-patch unsafe_block_signer implementation.
- No excerpt shows where the resolved signer is enforced in block validation, acceptance, or peer handling.
