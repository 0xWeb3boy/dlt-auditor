# Code-Shape Card

## Metadata

- ID: `solana-2021-04-06-solana-transaction-processing-03d3ae1cb9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`

## Code Shape Summary

The supported finding is faucet airdrop resource-control hardening. The patch changes cap and slice semantics toward per-IP handling, adds peer-address handling/logging in the faucet server path, and improves faucet-specific error reporting. The evidence does not establish a consensus, replay, signature-validation, or memory-safety vulnerability.

## Search Motifs

- search for resource control hardening checks near transaction-processing entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Bind resource-allocation limits to an explicit requester identity and preserve domain-specific faucet errors for callers.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
