# Validation Card

## Metadata

- ID: `sui-2023-02-21-sui-transaction-processing-d965c19fd2`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## What Confirmed The Issue

- Unchecked aggregation of payment amounts was replaced with checked addition and explicit overflow rejection.
- The guarded value is used by check_total_coins before pay() calls debit_coins_and_transfer.
- A regression test covers an overflowing amount list using u64::MAX plus another value.
- The new ExecutionFailureStatus::TotalAmountOverflow makes overflow an expected validation failure.

## What Could Have Invalidated It

- No debit_coins_and_transfer implementation evidence proving funds could be stolen or minted.
- No end-to-end transaction acceptance or consensus impact evidence.
- No evidence of remote crash, panic, or sustained denial of service.
- No proof that the overflow was reachable from an untrusted external transaction format beyond the pay path context.

## Severity Guidance

- Expected impact band: asset-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Keep as security-hardening, not a proven security-fix exploit case.
- Supported claim is unchecked monetary amount aggregation in transaction validation.
- Do not claim liveness impact from the provided evidence.
- Do not claim theft, minting, authorization bypass, signature bypass, or consensus failure.
