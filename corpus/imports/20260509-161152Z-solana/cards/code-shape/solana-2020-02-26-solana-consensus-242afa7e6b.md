# Code-Shape Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-242afa7e6b`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-bootstrap-data-validation`

## Code Shape Summary

The evidence supports a likely security fix in Solana validator bootstrap. The commit subject states that genesis config downloaded over RPC is now validated before acceptance, and the snippets show the genesis path changed from a generic ledger download into a dedicated `download_genesis` function that receives `ValidatorConfig`. The exact validation predicate is not shown, so the finding should not claim a proven exploit or concrete consensus split.

## Search Motifs

- search for untrusted bootstrap data validation checks near consensus entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add a validation boundary around remotely supplied bootstrap state before it becomes the validator's accepted local genesis state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
