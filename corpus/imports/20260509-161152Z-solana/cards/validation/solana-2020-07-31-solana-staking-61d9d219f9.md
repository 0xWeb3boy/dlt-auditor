# Validation Card

## Metadata

- ID: `solana-2020-07-31-solana-staking-61d9d219f9`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`

## What Confirmed The Issue

- Commit message states withdraw authority signature could imply custodian signature and lockup would not be enforced.
- Core stake lockup check changed from `signers.contains(&self.custodian)` to explicit `custodian == Some(&self.custodian)`.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
