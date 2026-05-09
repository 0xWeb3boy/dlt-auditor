# Root-Cause Card

## Metadata

- ID: `solana-2023-01-31-solana-cryptography-a5af54669a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The supported root cause is missing transaction-level enforcement of a bounded total loaded account data size in the runtime account-loading path. The evidence does not support claims about cryptography, replay protection, or signature validation.

## Impact Pattern

- Primary impact: resource-exhaustion
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds a feature-gated 64 MiB cap on total loaded account data during Solana transaction account loading and introduces a dedicated transaction error when the cap is exceeded. The evidence supports resource-control hardening in a critical runtime path, but does not establish a concrete exploit, crash, or network denial-of-service scenario.
