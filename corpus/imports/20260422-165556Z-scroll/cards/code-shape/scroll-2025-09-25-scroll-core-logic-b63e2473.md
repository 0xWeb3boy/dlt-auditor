# Code-Shape Card

## Metadata

- ID: `scroll-2025-09-25-scroll-core-logic-b63e2473`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-configuration-mismatch`

## Code Shape Summary

- Short description of what the buggy code looked like: The supplied evidence supports a correctness fix in verifier initialization and configuration plumbing: version is now carried explicitly and can be derived from fork name plus validium mode. That is plausibly relevant to PI-hash checking, but the snippets do not establish a concrete vulnerability, exploit path, or even whether the pre-fix behavior caused false accepts rather than only false rejects or misconfiguration.

## Search Motifs

- Motif 1: verifier config struct lacks explicit version and derives it late from loosely coupled metadata
- Motif 2: fork name and mode determine circuit selection in one layer but version plumbing lives elsewhere
- Motif 3: configuration object gains explicit version field to keep verifier initialization and proof context aligned

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Carry explicit version metadata through verifier configuration objects and derive it canonically from fork name plus validium mode when constructing verifier state.

## False Match Warnings

- Warning 1: If the verifier has a single immutable version source or always recomputes its effective config from canonical metadata, similar refactors may be lower risk.
- Warning 2: Version-carriage cleanup alone is not enough; the important signal is whether the verifier previously selected config from inconsistent sources.
- Warning 3: The evidence supports verifier hardening, not a proven false-accept bug.
