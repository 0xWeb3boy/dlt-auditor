# Code-Shape Card

## Metadata

- ID: `agave-2026-04-20-agave-transaction-processing-b9365a82f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-hardening`

## Code Shape Summary

- Transaction-view sanitization is split or incomplete, leaving version-specific size limits, signature/account consistency, duplicate-address rejection, and config/header checks unevenly enforced.

## Search Motifs

- sanitized transaction view missing duplicate address check
- signature count mismatch not rejected at sanitize boundary
- version-specific transaction size limit absent
- heap size config not checked during transaction sanitize

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Centralize sanitize flow and add explicit version-aware checks for size, signatures, accounts, duplicate addresses, headers, lookups, and config fields.

## False Match Warnings

- A canonical sanitizer already enforces the same invariants before any downstream use.
- The change only reorganizes comments or function order.
- Malformed inputs are rejected by deserialization before a transaction view exists.
