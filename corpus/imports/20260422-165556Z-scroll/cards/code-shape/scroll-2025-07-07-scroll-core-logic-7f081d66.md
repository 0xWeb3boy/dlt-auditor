# Code-Shape Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-7f081d66`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch adds fork-name normalization and an equality check in `gen_universal_task`, so chunk and batch tasks no longer proceed with an unchecked combination of `task_json` fork data and a separate fork-name string. The evidence supports a correctness/integrity fix around inconsistent fork-name handling, but it does not establish a concrete vulnerability or prior acceptance of invalid proofs.

## Search Motifs

- Motif 1: fork name supplied in both serialized task payload and explicit parameter
- Motif 2: normalization step added alongside an equality check between semantically duplicate fields
- Motif 3: task generator previously trusted stringly typed fork metadata from more than one source

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Normalize fork-name variants and fail closed when task JSON and explicit fork arguments disagree before generating universal tasks.

## False Match Warnings

- Warning 1: If the duplicated field is never attacker-controlled or never diverges semantically, a similar cleanup may be lower value.
- Warning 2: The important signal is not string normalization alone, but the added rejection of mismatched fork identity before task construction.
- Warning 3: The evidence supports consistency hardening, not a demonstrated acceptance of malformed proofs.
