# Validation Card

## Metadata

- ID: `solana-2022-12-02-solana-cryptography-87d939b319`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-cryptographic-key-derivation`

## What Confirmed The Issue

- Production ElGamal public-key derivation changed from secret scalar multiplication to inverse-scalar multiplication by H.
- The nonzero scalar assertion was moved into the canonical ElGamalPubkey::new derivation helper.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
