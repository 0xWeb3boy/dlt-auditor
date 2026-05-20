# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-purity-check-storage-write-opcode-32886`
- Bug family: `authz_and_role_gates`
- Bug class: `read-only-effect-gate-bypass`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if VM runtime enforces no-storage-write mode for read calls.
- No issue if the function is not externally reachable or has explicit authorization.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Users may safely call a function labeled read-only while it mutates state; exploitability depends on contract behavior.

## False-Positive Cautions

- No issue if VM runtime enforces no-storage-write mode for read calls.
- No issue if the function is not externally reachable or has explicit authorization.
