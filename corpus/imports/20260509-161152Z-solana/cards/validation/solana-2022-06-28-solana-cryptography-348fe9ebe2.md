# Validation Card

## Metadata

- ID: `solana-2022-06-28-solana-cryptography-348fe9ebe2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `late-network-input-validation`

## What Confirmed The Issue

- Commit body explicitly says invalid shred slot/parent checks occurred after sig-verify and deserialization, wasting resources.
- Fetch-stage packet discard now calls should_discard_shred before packet hashing and deduplication.

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
