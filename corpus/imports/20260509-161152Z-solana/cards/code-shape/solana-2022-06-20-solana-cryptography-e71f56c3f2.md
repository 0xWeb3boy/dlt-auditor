# Code-Shape Card

## Metadata

- ID: `solana-2022-06-20-solana-cryptography-e71f56c3f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-packet-slice-access`

## Code Shape Summary

The patch likely security-hardens Solana packet ingress and sigverify parsing by replacing raw packet byte indexing with a `Packet::data(...)` accessor that returns `Option`, forcing call sites to handle invalid offsets explicitly. The evidence supports bounds-checking hardening, not a proven signature bypass, replay flaw, memory corruption issue, or confirmed exploitable crash.

## Search Motifs

- search for unchecked packet slice access checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where consensus, accounting, or authorization-sensitive state is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace direct packet buffer indexing with a bounds-checked accessor returning `Option`, then require each call site to convert invalid offsets into the appropriate local failure behavior.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
