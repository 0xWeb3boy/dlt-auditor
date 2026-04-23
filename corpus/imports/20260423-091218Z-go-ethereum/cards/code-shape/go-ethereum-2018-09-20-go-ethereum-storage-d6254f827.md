# Code-Shape Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`

## Code Shape Summary

- A canonical-selection path uses randomness to break ties between otherwise equal competitors, and the fix replaces that randomness with a policy hook that can recognize locally trusted producers.

## Search Motifs

- Motif 1: Equal score or equal difficulty branch calls random selection.
- Motif 2: Constructor or state object grows an `isLocal`, `isTrusted`, or producer-classification callback.
- Motif 3: Same-height competitor logic changes while stronger-chain logic remains untouched.

## Typical Asymmetry

- The attacker only needs to produce an equal-ranked competitor, while the defender loses because the tie-break ignores local trust context.

## Patch Pattern

- Replace random tie-break behavior with explicit policy-aware canonical-selection rules that can inspect producer provenance or local trust.

## False Match Warnings

- Do not match deterministic protocol rules that already specify a tie-break outcome.
- Benchmarks and constructor call-site updates are supporting changes, not the core security logic.
