# Code-Shape Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-core-logic-fd99d9175`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- Stack-local borrowed-account wrappers were passed to helper macros without deterministic zero-initialization, leaving helper behavior dependent on stale stack bytes.

## Search Motifs

- Motif 1: stack-local guard struct zeroed before helper macro
- Motif 2: borrow wrapper initialized with {0}
- Motif 3: helper reads fields before explicit initialization

## Typical Asymmetry

- The runtime assumes helper inputs start from a clean state, but stack locals inherit whatever bytes were already present.

## Patch Pattern

- Zero-initialize helper structs at declaration time so every later helper path sees a consistent baseline state.

## False Match Warnings

- No macro or helper implementation is provided to show the exact field read before initialization.
- No exploit path, attacker-controlled stale stack data, or privilege impact is demonstrated.
