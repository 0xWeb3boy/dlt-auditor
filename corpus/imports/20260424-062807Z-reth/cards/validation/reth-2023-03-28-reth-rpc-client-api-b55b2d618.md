# Validation Card

## Metadata

- ID: `reth-2023-03-28-reth-rpc-client-api-b55b2d618`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-penalty-misclassification`

## What Confirmed The Issue

- PoolError::is_bad_transaction() is added specifically to distinguish permanently invalid transactions from pool-state or internal errors.
- The new helper's documentation says it is used to decide whether the original sender should be penalized.

## What Could Have Invalidated It

- The patch excerpts do not show what on_bad_import and on_good_import actually do downstream
- No evidence shows concrete peer disconnects, bans, or reputation score changes caused by the old behavior

## Severity Guidance

- Expected impact band: network_policy_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- The patch excerpts do not show what on_bad_import and on_good_import actually do downstream
- No evidence shows concrete peer disconnects, bans, or reputation score changes caused by the old behavior
