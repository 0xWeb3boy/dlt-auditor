# Validation Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-ef9f54b3d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-race`

## What Confirmed The Issue

- runtime/src/bank.rs changes register_tick from guarding only is_frozen() to guarding freeze_started(), preventing mutation during the freeze window.
- runtime/src/bank.rs moves tick_height.fetch_add until after block-boundary blockhash and recent-blockhash sysvar updates.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
