# Validation Card

## Metadata

- ID: `solana-2020-06-30-solana-cryptography-88eeb817e4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-restart-precondition-hardening`

## What Confirmed The Issue

- Validator startup path now exits when wait_for_supermajority reports an error.
- wait_for_supermajority distinguishes already-past, exact, and local-ledger-behind cases instead of silently returning for all mismatches.

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
