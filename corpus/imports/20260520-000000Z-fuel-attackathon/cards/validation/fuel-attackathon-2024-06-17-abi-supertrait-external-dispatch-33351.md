# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-abi-supertrait-external-dispatch-33351`
- Bug family: `authz_and_role_gates`
- Bug class: `supertrait-method-dispatch-exposure`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the method is intentionally listed in the public ABI.
- No issue if the exposed helper has complete independent authorization checks.

## Severity Guidance

- Expected impact band: `critical`
- Expected severity band: `critical`
- Rationale: Methods assumed to be internal can become public entrypoints, bypassing contract-level access-control assumptions.

## False-Positive Cautions

- No issue if the method is intentionally listed in the public ABI.
- No issue if the exposed helper has complete independent authorization checks.
