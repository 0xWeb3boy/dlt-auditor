# Validation Card

## Metadata

- ID: `solana-2021-02-13-solana-transaction-processing-99012f022e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-size-validation`

## What Confirmed The Issue

- Hash::from_str previously decoded the supplied string before enforcing the fixed 32-byte decoded size.
- The patch rejects inputs longer than MAX_BASE58_LEN before calling bs58::decode.

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
