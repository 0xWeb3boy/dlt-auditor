# Code-Shape Card

## Metadata

- ID: `nitro-2023-07-31-nitro-transaction-processing-dd22b5f05`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch tightens how the staker/validator path interprets execution state when deriving message counts and hashes. The evidence supports a protocol-correctness or hardening change, but it does not establish an exploitable vulnerability from the provided diff alone.

## Search Motifs

- Motif 1: message-count conversions accept non-boundary execution states
- Motif 2: hash domains are reused across semantically different states or edges
- Motif 3: state-derivation helpers gain explicit boundary-state preconditions after hardening

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Enforce stricter canonical-state preconditions, derive indices from the intended boundary state, and domain-separate hashes for semantically different states.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
