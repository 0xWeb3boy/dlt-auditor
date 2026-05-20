# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-call-frame-code-size-address-33451`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `call-frame-field-dereference-error`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if code_size is used only for logging.
- No issue if the function is documented and named as returning an address.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Contracts using code-size introspection for security can admit callers they meant to reject.

## False-Positive Cautions

- No issue if code_size is used only for logging.
- No issue if the function is documented and named as returning an address.
