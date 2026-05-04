# Validation Card

## Metadata

- ID: `stellar-core-2017-04-24-stellar-core-transaction-processing-00515f37c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-accounting-invariant`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- InflationOpFrame adds inflationAmount separate from amountToDole.
- The new ledger-version path increments totalCoins once by inflationAmount.
- Older behavior is explicitly gated to legacy versions.

## What Could Have Invalidated It

- If totalCoins is non-consensus telemetry only, severity drops.
- If feePool was not included in the old counter update, the core issue would be absent.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high_or_medium
- Rationale: Supply accounting is consensus critical, though the finding does not prove attacker control or direct profit, so high but not critical.

## False-Positive Cautions

- Do not flag monetary refactors unless aggregate counters and redistributed funds are mixed.
- Preserve protocol-version context when judging old ledger behavior.
