# Validation Card

## Metadata

- ID: `moonbeam-2023-02-07-moonbeam-transaction-processing-edf1a33ae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-call-policy-hardening`

## What Confirmed The Issue

- precompile_set dispatch paths changed comments and code to perform common checks.
- Proxy-specific precheck was removed while shared configuration expanded.

## What Could Have Invalidated It

- A formal equivalence proof that all old local checks matched the new shared checks
- The affected dispatch path was unreachable in production runtime

## Severity Guidance

- Expected impact band: precompile_policy_integrity
- Expected severity band: medium

## False-Positive Cautions

- Refactoring to shared checks is not a vulnerability if all old local checks were equivalent
- Pure view precompiles may tolerate broader call modes
