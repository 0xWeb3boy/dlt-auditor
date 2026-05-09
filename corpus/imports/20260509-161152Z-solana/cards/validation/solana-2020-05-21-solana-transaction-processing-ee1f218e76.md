# Validation Card

## Metadata

- ID: `solana-2020-05-21-solana-transaction-processing-ee1f218e76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-input-validation-panic-hardening`

## What Confirmed The Issue

- Client-controlled sendTransaction input reaches deserialize_bs58_transaction.
- The old code used bs58::decode(...).into_vec().unwrap() on that input.

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
