# Code-Shape Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-1869e1c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch in `crates/libzkp/src/lib.rs` adds canonicalization and an equality check for `fork_name` when building chunk and batch universal tasks. The code evidence supports a consistency fix at a protocol-sensitive boundary, but it does not establish that this previously enabled invalid proof acceptance, verifier bypass, or another concrete vulnerability.

## Search Motifs

- Motif 1: same semantic field passed both inside task json and as a separate function parameter
- Motif 2: fork or version string normalized in one path but not compared across all sources
- Motif 3: universal task builder trusts mismatched identifiers before constructing fork-specific config

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Normalize fork-name aliases and reject cross-field mismatches before building chunk or batch universal tasks from mixed task sources.

## False Match Warnings

- Warning 1: If only one canonical source of fork identity exists at runtime, a similar string-normalization change may be routine hygiene.
- Warning 2: String cleanup alone is not enough; the security-relevant part is whether mismatches could reach fork-specific proving logic.
- Warning 3: The evidence supports integrity hardening, not a demonstrated verifier bypass.
