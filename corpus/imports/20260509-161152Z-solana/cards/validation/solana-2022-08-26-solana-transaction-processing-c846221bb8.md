# Validation Card

## Metadata

- ID: `solana-2022-08-26-solana-transaction-processing-c846221bb8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-snapshot-validation`

## What Confirmed The Issue

- Adds `verify_slot_deltas(slot_deltas.as_slice(), &bank)?` before `bank.src.append(&slot_deltas)` during snapshot bank rebuild.
- New validation checks snapshot slot deltas for corruption/invalidity and compares them against bank slot history.

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
