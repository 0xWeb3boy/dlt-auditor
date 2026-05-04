# Validation Card

## Metadata

- ID: `avalanchego-2026-04-30-avalanchego-p2p-networking-a9c2157265`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-allowlist-admission-gap`

## What Confirmed The Issue

- Evidence: New Admitter interface explicitly gates inbound transactions for the mempool.
- Evidence: addToPool now filters transactions through the configured admitter before forwarding survivors to txpool.Add.
- Evidence: Subnet EVM test asserts a non-admin NoRole sender is rejected at SendTransaction/RPC mempool ingress.

## What Could Have Invalidated It

- Compensating control: No full implementation hunk for sae/admitter.go is provided.
- Compensating control: No evidence proves unauthorized transactions could previously execute in accepted blocks.
- Compensating control: No evidence supports malformed input crash, cryptographic validation, replay, or remote DoS claims.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: medium_or_low
- Severity rationale: Missing allowlist enforcement at mempool ingress can admit policy-forbidden transactions, but the record does not prove block execution or consensus bypass.

## False-Positive Cautions

- Caution: Validate only as allow-list transaction admission hardening.
- Caution: Do not claim a confirmed consensus or block execution authorization bypass.
- Caution: Do not classify as liveness-failure based on the supplied evidence.
