# Code-Shape Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-89d2f34a03`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`

## Code Shape Summary

The patch appears to harden the Solana vote-program withdraw path by adding Rent context under the `reject_non_rent_exempt_vote_withdraws` feature and changing withdrawal handling around the remaining vote-account balance. The supplied evidence supports a rent-exemption invariant fix, but does not establish an exploit, theft, signer bypass, memory issue, or demonstrated consensus failure.

## Search Motifs

- search for protocol invariant enforcement checks near consensus entrypoints
- compare validation before and after the rent-exemption-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Thread required sysvar context into the state-transition path under a feature gate, compute the post-withdrawal balance explicitly, and reject invalid partial-withdrawal results when Rent validation is available.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
