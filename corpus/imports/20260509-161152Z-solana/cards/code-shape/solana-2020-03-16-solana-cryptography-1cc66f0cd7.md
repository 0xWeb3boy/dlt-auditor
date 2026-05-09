# Code-Shape Card

## Metadata

- ID: `solana-2020-03-16-solana-cryptography-1cc66f0cd7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-consistency-hardening`

## Code Shape Summary

The patch adds optional validator hardening for accounts-state consistency. It introduces an accounts hash verifier path, CRDS handling for accounts hash gossip values, and a CLI/config flag that can halt a validator when a mismatch is detected against configured trusted validators. The evidence does not establish an exploitable vulnerability or prove that the previous behavior violated a security property, so this should not be treated as a confirmed s...

## Search Motifs

- search for validator state consistency hardening checks near cryptography entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add configuration-gated runtime consistency checking: publish local accounts-state hashes, compare them with trusted-validator gossip values, and optionally fail stop on mismatch.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
