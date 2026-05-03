# Code-Shape Card

## Metadata

- ID: `firedancer-2026-02-23-firedancer-cryptography-3e0535b19`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-block-resource-exhaustion`

## Code Shape Summary

- Replay accounting used ordinary unsigned accumulation in a path where malformed block input could make the counter wrap and mask excessive work.

## Search Motifs

- Motif 1: saturating add replaces plain unsigned add
- Motif 2: eager tick/hash validation moved earlier in scheduler path
- Motif 3: resource counter overflow could hide malformed-block cost

## Typical Asymmetry

- The attacker controls block progress shape, but the scheduler assumes counters stay within normal operational ranges.

## Patch Pattern

- Validate malformed progress conditions early and use saturating arithmetic so excessive work cannot be hidden by wraparound.

## False Match Warnings

- No proof of a concrete exploit path or attacker-controlled delivery boundary beyond malformed block data is shown.
- No evidence supports signature forgery, replay-authentication bypass, or access-control impact.
