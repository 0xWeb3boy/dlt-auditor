# Validation Card

## Metadata

- ID: `solana-2020-09-15-solana-core-logic-b5c7ad3a9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-network-exposure-hardening`

## What Confirmed The Issue

- Restricted repair-only mode suppresses ip_echo TCP listener registration.
- Restricted repair-only mode rewrites multiple unused advertised validator service addresses to 0.0.0.0:0.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
