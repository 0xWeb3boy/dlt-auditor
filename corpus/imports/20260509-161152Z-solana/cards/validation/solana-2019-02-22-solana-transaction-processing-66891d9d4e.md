# Validation Card

## Metadata

- ID: `solana-2019-02-22-solana-transaction-processing-66891d9d4e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Commit body says other accounts should not be able to modify system account userdata.
- Storage entrypoint changed from requiring two keyed accounts to one keyed account.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
