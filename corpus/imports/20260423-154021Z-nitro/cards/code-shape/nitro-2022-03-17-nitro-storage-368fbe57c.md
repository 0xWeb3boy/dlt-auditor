# Code-Shape Card

## Metadata

- ID: `nitro-2022-03-17-nitro-storage-368fbe57c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `configuration-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible patch adds fail-fast validation in the validator startup path, including configuration sanity checks and a runtime WASM module-root comparison.

## Search Motifs

- Motif 1: startup validation grows new sanity checks for mutually dependent config knobs
- Motif 2: runtime-loaded artifacts are measured after load but not compared to configured identity
- Motif 3: validator startup proceeds even when DA mode or module-root assumptions are inconsistent

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Add fail-fast startup validation for critical configuration dependencies and verify that the runtime-loaded validator artifact matches the expected configured identity.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
