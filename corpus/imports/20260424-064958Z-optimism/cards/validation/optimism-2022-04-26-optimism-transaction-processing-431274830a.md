# Validation Card

## Metadata

- ID: `optimism-2022-04-26-optimism-transaction-processing-431274830a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `denial-of-service`

## What Confirmed The Issue

- Before the patch, a single deposit derivation error caused createNewBlock and insertEpoch to return an error and stop processing.
- After the patch, deposit derivation returns partial results plus []error, allowing valid deposits to continue.
- UserDeposits now records malformed deposit log errors per receipt/log instead of aborting the whole batch.
- DeriveDeposits now records encoding failures per deposit instead of failing the entire derivation step.

## What Could Have Invalidated It

- The provided hunks do not show the claimed contract-side gasLimit narrowing from uint256 to uint64.
- The patch alone does not prove an external attacker could reliably trigger the malformed deposit condition in practice.
- The evidence does not show exploitation, consensus break, or direct fund theft.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- The provided hunks do not show the claimed contract-side gasLimit narrowing from uint256 to uint64.
- The patch alone does not prove an external attacker could reliably trigger the malformed deposit condition in practice.
- The evidence does not show exploitation, consensus break, or direct fund theft.
