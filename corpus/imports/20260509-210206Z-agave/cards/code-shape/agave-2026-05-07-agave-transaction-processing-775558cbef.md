# Code-Shape Card

## Metadata

- ID: `agave-2026-05-07-agave-transaction-processing-775558cbef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- A transaction parser validates static account counts against an ambiguous max and uses fixed helper arrays whose size may not match the full u8 program-id index domain.

## Search Motifs

- txv1 OOB static account count
- MAX_STATIC_ACCOUNTS differs from format-specific packet max
- u8 program_id_index indexes fixed flags array
- FILTER_SIZE should cover 256 possible indexes

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Use transaction-format-specific account-count limits and size fixed helper caches for the complete accepted index domain.

## False Match Warnings

- The language/runtime bounds-checks every index and converts failures to clean parse errors.
- The parser rejects out-of-range counts before helper arrays are accessed.
- The changed constants only rename equivalent bounds.
