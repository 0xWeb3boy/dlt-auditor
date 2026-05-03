# Code-Shape Card

## Metadata

- ID: `firedancer-2026-01-22-firedancer-cryptography-b76fbe370`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-poh-validation`

## Code Shape Summary

- Block completion treated PoH verification as an implicit later assumption instead of a required gate before normal replay progression.

## Search Motifs

- Motif 1: verify_ticks called before block-end emission
- Motif 2: block marked dead when tick verification fails
- Motif 3: snapshot hashes_per_tick default changed to preserve verification semantics

## Typical Asymmetry

- Replay state wants to keep progressing, but PoH validity must be re-established before any completed block is trusted.

## Patch Pattern

- Move tick verification directly into the block-completion gate and preserve exact PoH parameters instead of substituting permissive defaults.

## False Match Warnings

- No concrete exploit path or attacker-controlled input flow is shown.
- No proof that invalid PoH or tick structure previously reached finalized consensus state is supplied.
