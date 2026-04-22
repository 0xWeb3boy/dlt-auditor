# Code-Shape Card

## Metadata

- ID: `base-2025-08-20-base-cryptography-0c207fc7f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: The caller did not fully enforce the verifier's return contract. It treated the absence of an error as sufficient instead of requiring the verifier's explicit success value from a `Result<bool, _>` API.

## Search Motifs

- Motif 1: verification result is partially interpreted instead of requiring explicit success
- Motif 2: one proof element or branch is trusted without recomputing the canonical expected value
- Motif 3: validation logic treats malformed or mismatched proof structure as recoverable instead of rejecting it

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Replace error-only handling of a verifier result with explicit success-state enforcement at the acceptance boundary.

## False Match Warnings

- What looks similar but is often not a bug: The patch supports that invalid-proof results were not explicitly rejected before this change.
