# Validation Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-242afa7e6b`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-bootstrap-data-validation`

## What Confirmed The Issue

- Commit subject states genesis config downloaded over RPC is validated before acceptance.
- Validator bootstrap code changes from generic ledger download to dedicated `download_genesis` with access to `ValidatorConfig`.

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
