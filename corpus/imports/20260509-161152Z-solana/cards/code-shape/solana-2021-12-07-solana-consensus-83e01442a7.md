# Code-Shape Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-83e01442a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-invariant-hardening`

## Code Shape Summary

The patch changes Solana vote-program withdrawal handling to compute the post-withdraw balance and to pass optional Rent sysvar context into `vote_state::withdraw` when the `reject_non_rent_exempt_vote_withdraws` feature is active. This is plausibly security-relevant state-validity hardening, but the supplied evidence does not show the actual rent-exemption rejection conditional or establish an exploitable vulnerability. Treat as unclear rather than a c...

## Search Motifs

- search for rent exemption invariant hardening checks near consensus entrypoints
- compare validation before and after the rent-exemption-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Make the post-withdraw balance explicit and pass required sysvar context into the state-transition function under a feature gate.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
