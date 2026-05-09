# Validation Card

## Metadata

- ID: `solana-2022-02-24-solana-storage-97d40ba3da`
- Bug family: `authz_and_role_gates`
- Bug class: `rent-state-validation-bypass`

## What Confirmed The Issue

- Commit subject states that resized accounts must be rent exempt.
- RentState::from_account classifies non-rent-exempt accounts as RentPaying(data_size), preserving data length as part of validation state.

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
