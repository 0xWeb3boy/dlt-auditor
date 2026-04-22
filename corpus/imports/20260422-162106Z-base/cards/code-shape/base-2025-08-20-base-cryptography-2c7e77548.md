# Code-Shape Card

## Metadata

- ID: `base-2025-08-20-base-cryptography-2c7e77548`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-verification-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The root cause is misuse of a verification API that reports semantic failure as `Ok(false)` rather than `Err(...)`. The pre-patch code checked only for API error propagation and ignored the boolean verification outcome.

## Search Motifs

- Motif 1: verification result is partially interpreted instead of requiring explicit success
- Motif 2: one proof element or branch is trusted without recomputing the canonical expected value
- Motif 3: validation logic treats malformed or mismatched proof structure as recoverable instead of rejecting it

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace error-only handling of `Result<bool>` verification routines with explicit acceptance checks that require `Ok(true)` before admitting data.

## False Match Warnings

- What looks similar but is often not a bug: The patch supports a cryptographic verification-handling flaw, not a proven `state-corruption` bug.
