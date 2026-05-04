# Validation Card

## Metadata

- ID: `snarkvm-2025-06-24-snarkvm-consensus-638f5f69c`
- Bug family: `authz_and_role_gates`
- Bug class: `reserved-locator-validation-hardening`

## What Confirmed The Issue

- The check for program-mediated `credits.aleo/upgrade` calls was moved into deployment-wide verification.
- Tests were updated to distinguish permitted direct user calls from disallowed program calls.

## What Could Have Invalidated It

- The reserved call is harmless or fully permission-checked at runtime.
- The moved check is purely a comment or rename with no broader invocation path.

## Severity Guidance

- Expected impact band: deployment_validation_and_upgrade_integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- The reserved function performs its own caller authorization for all indirect calls.
- The deployment format cannot encode the reserved locator in executable code.
