# Code-Shape Card

## Metadata

- ID: `solana-2019-08-21-solana-storage-e2d6f01ad3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-genesis-blockhash-validation`

## Code Shape Summary

The patch adds a validator startup check that compares the local ledger's genesis blockhash with an expected genesis blockhash obtained through the cluster entrypoint path. This is plausibly security-relevant cluster identity hardening, but the supplied evidence does not establish an exploitable vulnerability, attacker control, or concrete protocol impact, so it should not be treated as a confirmed security fix.

## Search Motifs

- search for missing genesis blockhash validation checks near storage entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Thread an expected identity value from bootstrap configuration into initialization, then validate the local state against it before constructing runtime state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
