# Code-Shape Card

## Metadata

- ID: `firedancer-2025-03-05-firedancer-consensus-97c08c390`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-bound-hardening`

## Code Shape Summary

- Consensus math fed a confirmation counter into power-of-two logic before proving it was within the protocol’s lockout history bound.

## Search Motifs

- Motif 1: pow2/shift applied to state-derived counter
- Motif 2: MAX_* history bound introduced before exponentiation
- Motif 3: confirmation count or lockout level clamped before arithmetic

## Typical Asymmetry

- Consensus state grows over time, but arithmetic helpers assume counters are still within their design-time bounds.

## Patch Pattern

- Clamp the counter to the protocol maximum before any arithmetic that can overflow or allocate oversized state.

## False Match Warnings

- No proof that normal execution can produce confirmation_count greater than MAX_LOCKOUT_HISTORY.
- No concrete exploit path or attacker-controlled input flow is shown.
