# Code-Shape Card

## Metadata

- ID: `solana-2020-04-16-solana-consensus-66abe45ea1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-consistency-monitoring`

## Code Shape Summary

The patch decouples accounts hash calculation from snapshot package generation and adds interval validation. The evidence supports a correctness and state-monitoring improvement in the accounts-hash/snapshot path, but it does not establish an exploitable vulnerability or a concrete security failure. Treat it as security-relevant but unproven rather than a confirmed security fix.

## Search Motifs

- search for state consistency monitoring checks near consensus entrypoints
- compare validation before and after the snapshot-integrity-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Separate accounts hash production from snapshot artifact generation, then validate interval configuration at startup.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
