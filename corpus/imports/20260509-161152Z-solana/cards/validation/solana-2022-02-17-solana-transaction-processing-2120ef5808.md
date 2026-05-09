# Validation Card

## Metadata

- ID: `solana-2022-02-17-solana-transaction-processing-2120ef5808`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-lifecycle-hardening`

## What Confirmed The Issue

- ed25519 precompile gating changes from `ed25519_program_enabled` to `prevent_calling_precompiles_as_programs`.
- Runtime genesis builtins add `ed25519_program` with `dummy_process_instruction`, matching precompile program lifecycle handling.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
