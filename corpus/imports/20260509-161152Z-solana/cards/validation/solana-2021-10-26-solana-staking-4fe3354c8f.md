# Validation Card

## Metadata

- ID: `solana-2021-10-26-solana-staking-4fe3354c8f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-sysvar-account-input`

## What Confirmed The Issue

- Adds load_current_index_checked(AccountInfo) with check_id validation before reading sysvar data.
- Adds get_instruction_relative(AccountInfo) with sysvar identity validation and invalid-index error behavior.

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
