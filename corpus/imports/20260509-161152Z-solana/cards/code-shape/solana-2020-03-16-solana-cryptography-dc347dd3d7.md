# Code-Shape Card

## Metadata

- ID: `solana-2020-03-16-solana-cryptography-dc347dd3d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-consistency-hardening`

## Code Shape Summary

The evidence supports an opt-in Solana validator accounts-hash consistency check that can halt a node on mismatch with configured trusted validators. It does not establish a concrete vulnerability, attacker path, default exposure, or prior exploitable consensus failure. Treat this as potentially security-relevant hardening, not a validated vulnerability fix.

## Search Motifs

- search for validator state consistency hardening checks near cryptography entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where network resource allocation, peer metadata acceptance, repair scheduling, or packet fanout is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an optional runtime consistency check for validator accounts-state hashes, carry the relevant digest through gossip/CRDS, require a trusted-validator comparison set, and halt when the configured mismatch condition is detected.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
