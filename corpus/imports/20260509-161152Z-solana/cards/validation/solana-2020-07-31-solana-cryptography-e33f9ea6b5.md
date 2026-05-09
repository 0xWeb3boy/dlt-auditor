# Validation Card

## Metadata

- ID: `solana-2020-07-31-solana-cryptography-e33f9ea6b5`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`

## What Confirmed The Issue

- Commit message states withdraw authority signature could imply custodian signature when both used the same public key, causing lockup not to be enforced.
- Lockup::is_in_force changed from checking signers.contains(custodian) to checking an explicit optional custodian pubkey.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
