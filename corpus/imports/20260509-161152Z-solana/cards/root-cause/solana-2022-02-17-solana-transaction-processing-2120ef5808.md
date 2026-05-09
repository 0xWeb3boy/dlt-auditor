# Root-Cause Card

## Metadata

- ID: `solana-2022-02-17-solana-transaction-processing-2120ef5808`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-lifecycle-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-consistency`

## Violated Invariant

- Protocol input must satisfy state transition consistency before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The provided evidence indicates inconsistent lifecycle handling for the ed25519 precompile program ID across runtime builtin registration, precompile feature gating, and feature-based builtin removal. It does not prove that this inconsistency allowed forged signatures, replay, unauthorized state mutation, or another concrete exploit.

## Impact Pattern

- Primary impact: security-boundary-hardening
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch aligns ed25519 precompile handling with the runtime builtin lifecycle used for precompile program IDs. It adds an `ed25519_program` dummy builtin, changes the ed25519 precompile feature gate to `prevent_calling_precompiles_as_programs`, and adds feature-based removal of the ed25519 builtin. The evidence supports a precompile/runtime feature-gating mismatch, but it does not establish an exploitable vulnerability or a concrete security failure.
