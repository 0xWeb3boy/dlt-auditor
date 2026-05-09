# Validation Card

## Metadata

- ID: `solana-2020-12-17-solana-cryptography-ff728e5e56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-undercheck`

## What Confirmed The Issue

- Deploy validation changed from rent based on fixed UpgradeableLoaderState::program_len() to rent based on program.data_len().
- A new guard rejects Program accounts whose data length is smaller than the required Program state length.

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
