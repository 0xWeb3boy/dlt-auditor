# Validation Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-4649378f95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-gating`

## What Confirmed The Issue

- Final vote condition now requires `switch_threshold`.
- Failure reporting now records `FailedSwitchThreshold` when the predicate fails.

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
