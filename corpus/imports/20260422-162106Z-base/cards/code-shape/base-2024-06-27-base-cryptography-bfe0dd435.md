# Code-Shape Card

## Metadata

- ID: `base-2024-06-27-base-cryptography-bfe0dd435`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible root issue is incomplete or less explicit verification logic in the oracle validation path, especially for `PreimageKeyType::Precompile`. However, the evidence also shows routine type-conversion adjustments, so the patch does not cleanly isolate a proven security bug as opposed to correctness or implementation completion work.

## Search Motifs

- Motif 1: verification result is partially interpreted instead of requiring explicit success
- Motif 2: one proof element or branch is trusted without recomputing the canonical expected value
- Motif 3: validation logic treats malformed or mismatched proof structure as recoverable instead of rejecting it

## Typical Asymmetry

- What was checked in one path but missing in another: The code performed some validation or normalization up front, but a later reuse, reconstruction, or alternate branch could still reach the sink without the exact same property being enforced.

## Patch Pattern

- What the fix changed structurally: Add explicit recomputation and assertion in a verification path, while normalizing key handling to a canonical typed representation.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the patch hardens verification of precompile-backed oracle entries by recomputing and checking expected outputs.
