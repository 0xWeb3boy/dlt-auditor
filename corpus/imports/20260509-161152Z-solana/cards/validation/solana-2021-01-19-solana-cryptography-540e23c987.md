# Validation Card

## Metadata

- ID: `solana-2021-01-19-solana-cryptography-540e23c987`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-locking-invariant`

## What Confirmed The Issue

- Loader upgrade processing now rejects a non-writable program account when the prevent_upgrade_and_invoke feature is active.
- The SDK upgrade instruction builder changed the program account from read-only to writable.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
