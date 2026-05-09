# Code-Shape Card

## Metadata

- ID: `solana-2020-05-28-solana-rpc-client-api-bc86ee8d13`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `repair-response-gating-bypass`

## Code Shape Summary

The patch likely fixes a denial-of-service or repair-gating issue in `ServeRepair::run_orphan`. The grounded change is that a failed repair response packet construction now stops the orphan walk, and tests assert that no nonce after `UNLOCK_NONCE_SLOT` yields no response.

## Search Motifs

- search for repair response gating bypass checks near rpc-client-api entrypoints
- compare validation before and after the nonce-state-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Terminate traversal when a gated response cannot be constructed, instead of treating the failed response as a skipped slot.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
