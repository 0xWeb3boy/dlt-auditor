# Code-Shape Card

## Metadata

- ID: `solana-2022-06-03-solana-transaction-processing-5ee157f43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-domain-collision`

## Code Shape Summary

The commit fixes a replay-domain collision between Solana durable nonce values and normal blockhashes. The commit message explicitly states that AdvanceNonceAccount could update a nonce to a raw blockhash, allowing a durable transaction to be executed both as a normal transaction and as a nonce transaction when that blockhash was used as recent_blockhash. The patch separates the domains and updates observed runtime and CLI nonce consumers to use the non...

## Search Motifs

- search for replay domain collision checks near transaction-processing entrypoints
- compare validation before and after the nonce-state-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Domain-separate replay identifiers used by distinct transaction acceptance paths, then update nonce readers to consume the domain-separated nonce value rather than the raw stored blockhash field.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
