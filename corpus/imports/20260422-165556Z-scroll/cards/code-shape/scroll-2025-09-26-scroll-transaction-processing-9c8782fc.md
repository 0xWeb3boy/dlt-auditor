# Code-Shape Card

## Metadata

- ID: `scroll-2025-09-26-scroll-transaction-processing-9c8782fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-missing`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided evidence supports a validium-task correctness fix, not a proven vulnerability fix. The coordinator now explicitly constructs a validium batch header for batch tasks, and the prover now sanity-checks that the header's recomputed hash matches the stored hash. That is an internal integrity/correctness improvement in the proving pipeline, but the snippets do not establish external attacker control or a concrete security impact.

## Search Motifs

- Motif 1: task builder uses stored batch hash without reconstructing or validating canonical header bytes
- Motif 2: validium-specific proving path diverges from canonical batch-header construction
- Motif 3: prover adds recomputed-hash sanity check after task detail grows a new header field

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Construct the validium batch header explicitly in the coordinator and reject tasks in the prover when the recomputed header hash differs from the stored batch identity.

## False Match Warnings

- Warning 1: If downstream verification always recomputes and binds the same header hash, a similar task-building bug may remain a correctness-only issue.
- Warning 2: Header-serialization refactors are not enough; the real signal is whether the stored hash and canonical header can diverge before proving.
- Warning 3: The evidence supports integrity hardening, not a demonstrated forged-batch exploit.
