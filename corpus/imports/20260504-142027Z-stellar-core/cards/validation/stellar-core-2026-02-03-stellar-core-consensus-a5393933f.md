# Validation Card

## Metadata

- ID: `stellar-core-2026-02-03-stellar-core-consensus-a5393933f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- TransactionQueue::canAdd gained validateHostFn before accepting pending status.
- TransactionFrame adds validateHostFn and maps failure to txSOROBAN_INVALID.
- Fee-bump validation delegates host-function checks to the wrapped transaction.

## What Could Have Invalidated It

- If invalid host functions cannot be constructed by external transactions, impact is low.
- If all validators reject the same malformed transaction later before consensus, the queue gap is availability or consistency hardening.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Missing validation at consensus-adjacent boundaries is security relevant, but the exact malformed condition and exploit impact are not proven.

## False-Positive Cautions

- Do not flag validation helper extraction without a newly covered boundary.
- Separate malformed host-function rejection from unrelated Soroban memo validation.
