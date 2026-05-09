# Validation Card

## Metadata

- ID: `solana-2020-04-16-solana-consensus-66abe45ea1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-consistency-monitoring`

## What Confirmed The Issue

- Accounts hash calculation is decoupled from snapshot package generation in the rooted bank path.
- The verifier records account hashes and can trigger halt behavior on trusted-validator account-hash mismatch.

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
