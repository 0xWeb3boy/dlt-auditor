# Code-Shape Card

## Metadata

- ID: `solana-2020-09-15-solana-core-logic-b5c7ad3a9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-network-exposure-hardening`

## Code Shape Summary

The patch adds validator startup options for more restrictive deployments, including a restricted repair-only mode and a gossip validator allowlist. The evidence supports network exposure reduction and configuration hardening, but not a confirmed vulnerability fix.

## Search Motifs

- search for validator network exposure hardening checks near core-logic entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add opt-in configuration controls that reduce validator network exposure in restricted deployments.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
