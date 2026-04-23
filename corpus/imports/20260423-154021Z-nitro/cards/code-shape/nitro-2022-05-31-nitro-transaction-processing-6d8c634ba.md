# Code-Shape Card

## Metadata

- ID: `nitro-2022-05-31-nitro-transaction-processing-6d8c634ba`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-initialization-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided evidence shows a configuration-binding fix: the code now carries `genesisBlockNum` through chain-config selection and checks it against the init message during startup. That supports a correctness or consensus-hardening interpretation, but the supplied material does not establish a concrete vulnerability or attacker-driven exploit path.

## Search Motifs

- Motif 1: genesis identifiers are threaded through config lookup only after bugs are found
- Motif 2: startup accepts init messages without cross-checking configured genesis metadata
- Motif 3: config selection keys omit a chain identity field that later code assumes is bound

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Add the missing identity field to configuration handling, thread it through config lookup paths, and reject mismatches during initialization.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
