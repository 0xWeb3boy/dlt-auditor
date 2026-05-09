# Validation Card

## Metadata

- ID: `solana-2020-03-16-solana-cryptography-1cc66f0cd7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-consistency-hardening`

## What Confirmed The Issue

- New accounts_hash_verifier service is described as comparing accounts-state hashes with trusted validators.
- New CLI flag enables halting on trusted-validator accounts hash mismatch.

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
