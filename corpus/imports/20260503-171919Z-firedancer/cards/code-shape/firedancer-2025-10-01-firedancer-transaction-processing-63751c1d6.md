# Code-Shape Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-transaction-processing-63751c1d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`

## Code Shape Summary

- The lookup path relied on a root or null transaction context even though replay could swap the underlying state before the address table read completed.

## Search Motifs

- Motif 1: comments or code mention TOCTOU or root-swap near a lookup path
- Motif 2: slot-derived transaction snapshot replaces a NULL or root state handle
- Motif 3: path drops work when the contextual bank or snapshot is unavailable

## Typical Asymmetry

- The attacker shapes replay timing or lookup inputs, but the implementation assumes the shared root state is stable during the read.

## Patch Pattern

- Resolve lookups against a slot-scoped snapshot handle and fail closed whenever the required bank state is unavailable.

## False Match Warnings

- No advisory, issue discussion, or commit body states a security vulnerability.
- No exploit path or attacker-controlled timing is shown.
