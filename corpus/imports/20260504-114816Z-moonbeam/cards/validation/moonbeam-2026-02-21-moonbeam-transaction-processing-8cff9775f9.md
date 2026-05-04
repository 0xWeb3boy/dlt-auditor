# Validation Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-8cff9775f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `unprotected-transaction-admission`

## What Confirmed The Issue

- Runtime constants change AllowUnprotectedTxs from true to false on all relevant networks.
- Commit and test updates explicitly say unprotected/legacy no-chain-id transactions are forbidden.

## What Could Have Invalidated It

- Only non-production configurations had the permissive flag
- Another mandatory validation layer already rejected all unprotected txs

## Severity Guidance

- Expected impact band: replay_protection_policy
- Expected severity band: medium

## False-Positive Cautions

- Dev runtimes may allow unprotected txs for local testing
- Presence of legacy transaction support is not a bug if chain-id is required
