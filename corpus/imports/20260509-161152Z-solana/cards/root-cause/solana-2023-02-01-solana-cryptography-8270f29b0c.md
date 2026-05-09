# Root-Cause Card

## Metadata

- ID: `solana-2023-02-01-solana-cryptography-8270f29b0c`
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

The account-loading path lacked the newly added explicit accumulated loaded-account-data cap in the provided evidence. This is best characterized as missing or incomplete resource-limit enforcement, not a demonstrated cryptographic or replay-validation flaw.

## Impact Pattern

- Primary impact: denial-of-service, resource-exhaustion
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds a feature-gated cap on total loaded account data during Solana transaction account loading. The evidence supports resource-consumption hardening in the runtime account-loading path, not cryptography, replay, signature validation, consensus divergence, or proven exploitability.
