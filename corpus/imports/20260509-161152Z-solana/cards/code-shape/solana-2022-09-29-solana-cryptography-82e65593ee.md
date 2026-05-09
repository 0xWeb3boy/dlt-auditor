# Code-Shape Card

## Metadata

- ID: `solana-2022-09-29-solana-cryptography-82e65593ee`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-transaction-forwarding`

## Code Shape Summary

The patch filters or sanitizes invalid transaction and vote packets before adding them to forwarding batches, and updates buffer removal logic and tests around already-processed transactions. The evidence supports a correctness and resource-hygiene improvement in the forwarding path. It does not prove crashability, signature bypass, transaction forgery, downstream acceptance of invalid packets, or consensus failure.

## Search Motifs

- search for invalid transaction forwarding checks near cryptography entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move forwarding eligibility checks before staging: sanitize deserialized packets with active bank context, share sanitized transaction state with forwarding batch logic, and remove filtered packets from the unprocessed buffer.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
