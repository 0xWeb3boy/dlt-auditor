# Code-Shape Card

## Metadata

- ID: `solana-2021-04-06-solana-transaction-processing-f6780d72b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `faucet-rate-limit-scope`

## Code Shape Summary

The draft's replay, signature, consensus, and transaction-forgery framing is unsupported. The grounded change is faucet resource-limit behavior: the TCP handler now resolves the peer address before processing, the commit says cap and slice arguments were repurposed to apply per IP, and related client-side faucet errors were made more specific. This may be abuse-control hardening, but the supplied evidence does not prove a security vulnerability or explo...

## Search Motifs

- search for faucet rate limit scope checks near transaction-processing entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Scope faucet resource-control decisions to the observed peer address and use typed errors for clearer faucet failure handling.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
