# Validation Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-75e9e321de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-publication-race`

## What Confirmed The Issue

- Commit subject names a race between setting tick height and calculating accounts hash.
- runtime/src/bank.rs changes register_tick from checking only is_frozen() to freeze_started(), blocking ticks during in-progress freezing.

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
