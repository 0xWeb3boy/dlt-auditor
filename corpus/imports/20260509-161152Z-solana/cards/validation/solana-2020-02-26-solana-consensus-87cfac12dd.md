# Validation Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-87cfac12dd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `bootstrap-trust-validation`

## What Confirmed The Issue

- Commit subject explicitly says RPC-downloaded genesis config is validated before acceptance.
- Generic `download_ledger` handling is replaced with `download_genesis` that receives `ValidatorConfig`.

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
