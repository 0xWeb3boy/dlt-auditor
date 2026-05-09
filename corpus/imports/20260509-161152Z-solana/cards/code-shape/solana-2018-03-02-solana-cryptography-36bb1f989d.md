# Code-Shape Card

## Metadata

- ID: `solana-2018-03-02-solana-cryptography-36bb1f989d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `double-spend-stale-accounting`

## Code Shape Summary

Confirmed security fix for a double-spend window in the accountant/historian transaction path. The commit explicitly states that a client could spend funds before the accountant processed a previous spend, and the patch moves signed-event validation into the accountant path while updating balances immediately rather than depending only on later historian processing.

## Search Motifs

- search for double spend stale accounting checks near cryptography entrypoints
- compare balance checks against the point where accepted spends reserve or update state
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for delayed logging, batching, or historian pipelines that lag spend-accounting state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance mutation, spend acceptance, and signature reservation are finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move validation and state reservation/update ahead of delayed logging or processing, so accepted spends immediately affect the balance state used by subsequent spend checks.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
