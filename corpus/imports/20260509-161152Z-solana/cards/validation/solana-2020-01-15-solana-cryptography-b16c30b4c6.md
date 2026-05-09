# Validation Card

## Metadata

- ID: `solana-2020-01-15-solana-cryptography-b16c30b4c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-hash-alignment-bug`

## What Confirmed The Issue

- Fix changes append_accounts from using unshifted hashes to hashes sliced by infos.len(), matching the shifted account metadata slice.
- The affected code is AccountsDB storage for account data and account hashes, which feed bank/account hash verification.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: Medium
- Rationale: The impact primarily affects availability, liveness, or validator resource consumption rather than direct fund theft.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
