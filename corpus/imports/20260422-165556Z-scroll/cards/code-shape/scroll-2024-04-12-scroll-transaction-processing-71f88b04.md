# Code-Shape Card

## Metadata

- ID: `scroll-2024-04-12-scroll-transaction-processing-71f88b04`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-binding`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch changes blob construction so it computes an EIP-4844 blob versioned hash, appends that hash to the challenge preimage, and returns it to callers. That is a real cryptographic-binding change in the DA encoding path. However, the supplied evidence does not show the downstream `piHash` use, verifier behavior, or any concrete acceptance flaw, so the material supports a security-relevant hardening/fix thesis only weakly and does not establish an actual vulnerability end to end.

## Search Motifs

- Motif 1: constructor returns blob or commitment data but caller drops the canonical versioned hash
- Motif 2: challenge preimage assembled from chunks without the final canonical blob identifier
- Motif 3: EIP-4844 blob path computes a versioned hash late and fails to thread it into the proof-binding surface

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Return the canonical versioned blob hash from DA blob construction and include it explicitly in the challenge-binding data that downstream components consume.

## False Match Warnings

- Warning 1: If the downstream verifier always recomputes and enforces the same canonical hash before accepting the proof, a similar omission may be non-exploitable.
- Warning 2: Auxiliary refactors that only change return signatures are not enough; the real issue is whether the canonical hash reaches the challenge preimage.
- Warning 3: The evidence supports cryptographic hardening, not a proven end-to-end acceptance flaw.
