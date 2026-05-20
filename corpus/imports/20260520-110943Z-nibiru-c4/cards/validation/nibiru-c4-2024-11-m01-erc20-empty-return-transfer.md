# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m01-erc20-empty-return-transfer`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-erc20-return-decoding`

## What Confirmed The Issue

- Public C4 report section M-01 rated this as Medium.
- The report kept this as a non-low finding without a confirmed mitigation PR in the included mitigation scope.

## What Could Have Invalidated It

- No issue if the protocol explicitly excludes missing-return tokens.
- No issue if token deployment is constrained to compliant contracts.

## Severity Guidance

- Expected impact band: supported token conversion DoS
- Expected severity band: medium

## False-Positive Cautions

- No issue if the protocol explicitly excludes missing-return tokens.
- No issue if token deployment is constrained to compliant contracts.
- No issue if empty return data is already accepted after a non-reverting call.
