# Validation Card

## Metadata

- ID: `oasis-core-2019-11-08-oasis-core-transaction-processing-ba88a37cf`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-validator-set-minimum-check`

## What Confirmed The Issue

- Evidence 1: The patch propagates 'MinValidators' from scheduler parameters into the validator-election routine, adds an explicit undersized-set rejection in 'electValidators', and rejects non-positive 'MinValidators' during 'InitChain'.
- Evidence 2: The source finding states the invariant explicitly: If scheduler configuration specifies a minimum validator count, initialization and validator election should reject validator sets smaller than that floor.

## What Could Have Invalidated It

- Compensating control 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Compensating control 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if the same accounting or limit check is rerun immediately before the sink on every path.
- Caution 2: Not a match if downstream queue rejection cannot leave the transaction or request accepted in observable state.
