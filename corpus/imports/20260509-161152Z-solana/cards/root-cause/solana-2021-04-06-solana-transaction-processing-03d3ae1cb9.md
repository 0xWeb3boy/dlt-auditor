# Root-Cause Card

## Metadata

- ID: `solana-2021-04-06-solana-transaction-processing-03d3ae1cb9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`
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

The grounded issue is ambiguous or insufficiently explicit scoping of faucet allocation controls to a requester IP. The provided evidence supports an anti-abuse/resource-control hardening interpretation, not a proven exploitable validation flaw.

## Impact Pattern

- Primary impact: resource-abuse, rate-limit-bypass
- Expected band: availability_or_resource_exhaustion
- Severity guide: Low/Medium

## Short Reusable Lesson

The supported finding is faucet airdrop resource-control hardening. The patch changes cap and slice semantics toward per-IP handling, adds peer-address handling/logging in the faucet server path, and improves faucet-specific error reporting. The evidence does not establish a consensus, replay, signature-validation, or memory-safety vulnerability.
