# Validation Card

## Metadata

- ID: `solana-2021-01-21-solana-transaction-processing-9dd5d4407b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-bound-validation`

## What Confirmed The Issue

- Adds pre-decode length guard in Signature::from_str for strings longer than MAX_BASE58_SIGNATURE_LEN.
- Adds pre-decode length guard in Pubkey::from_str for strings longer than MAX_BASE58_LEN.

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
- The signature library or sanitized message type already commits the disputed field unconditionally.
