# Code-Shape Card

## Metadata

- ID: `solana-2021-10-15-solana-consensus-44ff30b65b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-repair-retry-hardening`

## Code Shape Summary

The patch adds retry handling for `DuplicateAncestorDecision::InvalidSample` and `SampleNotDuplicateConfirmed` in Solana's ancestor hashes service. This is plausibly consensus-adjacent recovery hardening, but the provided evidence does not establish a concrete security vulnerability, attacker-controlled trigger, or consensus safety failure. Treat it as unclear security relevance rather than a confirmed or likely security fix.

## Search Motifs

- search for consensus repair retry hardening checks near consensus entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit retryability predicate, preserve the affected slot across the decision boundary, and requeue retryable decisions into the existing repair scheduling pool.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
