# Code-Shape Card

## Metadata

- ID: `solana-2022-02-17-solana-transaction-processing-2120ef5808`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-lifecycle-hardening`

## Code Shape Summary

The patch aligns ed25519 precompile handling with the runtime builtin lifecycle used for precompile program IDs. It adds an `ed25519_program` dummy builtin, changes the ed25519 precompile feature gate to `prevent_calling_precompiles_as_programs`, and adds feature-based removal of the ed25519 builtin. The evidence supports a precompile/runtime feature-gating mismatch, but it does not establish an exploitable vulnerability or a concrete security failure.

## Search Motifs

- search for precompile lifecycle hardening checks near transaction-processing entrypoints
- compare validation before and after the state-transition-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Align feature gates and runtime registration/removal for a precompile program ID across the SDK precompile table and runtime builtin lifecycle.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
