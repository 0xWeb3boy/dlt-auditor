# Validation Card

## Metadata

- ID: `sui-2023-02-27-sui-transaction-processing-f88a9a6cb6`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## What Confirmed The Issue

- Pay transaction input coin balances were previously summed with unchecked u64 addition.
- Leftover coin balances after debit/transfer were also previously summed with unchecked u64 addition.
- The patch rejects overflowing aggregate coin balances with TotalCoinBalanceOverflow.
- The commit message states overflow may happen for non-SUI coins despite SUI supply bounds.

## What Could Have Invalidated It

- No evidence that an attacker could trigger overflow in production with valid assets.
- No evidence of theft, money creation, or balance manipulation before the fix.
- No evidence of process crash, denial of service, liveness failure, or consensus divergence.
- No details showing whether unchecked overflow wrapped in release builds for this configuration.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Treat as checked-arithmetic hardening for monetary accounting, not a proven exploit fix.
- Do not claim SUI coin supply itself could overflow u64.
- Do not claim liveness impact from the supplied evidence.
- Do not claim successful asset theft or consensus failure.
