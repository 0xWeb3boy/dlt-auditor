# Root-Cause Card

## Metadata

- ID: `solana-2021-04-06-solana-transaction-processing-f6780d72b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `faucet-rate-limit-scope`
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

The only supported root cause is ambiguous or changed faucet limit scoping: cap and slice behavior was changed to be per peer IP. The evidence does not show incomplete signature validation, replay protection failure, consensus impact, or arbitrary transaction creation.

## Impact Pattern

- Primary impact: resource-abuse, airdrop-abuse-control
- Expected band: availability_or_resource_exhaustion
- Severity guide: Low/Medium

## Short Reusable Lesson

The draft's replay, signature, consensus, and transaction-forgery framing is unsupported. The grounded change is faucet resource-limit behavior: the TCP handler now resolves the peer address before processing, the commit says cap and slice arguments were repurposed to apply per IP, and related client-side faucet errors were made more specific. This may be abuse-control hardening, but the supplied evidence does not prove a security vulnerability or explo...
