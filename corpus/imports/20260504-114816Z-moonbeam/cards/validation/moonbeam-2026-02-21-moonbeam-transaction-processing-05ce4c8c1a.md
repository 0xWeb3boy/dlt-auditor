# Validation Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-05ce4c8c1a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-protection-policy-hardening`

## What Confirmed The Issue

- AllowUnprotectedTxs changed to false in Moonbeam, Moonriver, and Moonbase runtimes.
- Related RPC boolean changed to false and tests moved away from chain-id-less legacy txs.

## What Could Have Invalidated It

- Runtime admission already rejected unprotected transactions despite the flag
- The network is a dev/test environment where replay protection is intentionally disabled

## Severity Guidance

- Expected impact band: replay_protection_policy
- Expected severity band: medium

## False-Positive Cautions

- Private/dev chains may intentionally allow legacy unprotected transactions
- Transactions with EIP-155 chain id are not in scope
