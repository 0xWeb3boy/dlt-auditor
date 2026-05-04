# Validation Card

## Metadata

- ID: `snarkvm-2025-03-05-snarkvm-consensus-204e8b564`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursion-resource-accounting-hardening`

## What Confirmed The Issue

- `get_number_of_calls` was rewritten to traverse the current call graph and enforce a maximum.
- Stack initialization now invokes the validation for inserted functions.

## What Could Have Invalidated It

- The cached values are cryptographically committed and verified against the current program.
- The recursion limit is enforced earlier at parsing with no dynamic call expansion.

## Severity Guidance

- Expected impact band: availability_and_resource_accounting
- Expected severity band: medium_or_low

## False-Positive Cautions

- The cache is immutable and recomputed on every program change.
- A later mandatory execution path enforces the same recursion bound before work is done.
