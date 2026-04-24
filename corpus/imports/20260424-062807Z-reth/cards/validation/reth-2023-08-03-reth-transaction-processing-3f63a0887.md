# Validation Card

## Metadata

- ID: `reth-2023-08-03-reth-transaction-processing-3f63a0887`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement`

## What Confirmed The Issue

- Commit subject states the intent: only propagate transactions that are allowed to be propagated.
- add_transaction carries a propagate field from validation into ValidPoolTransaction, showing propagation is an explicit policy decision.

## What Could Have Invalidated It

- The provided excerpt does not show the rest of on_new_pending_transaction, so actual enforcement using propagate_allowed is not visible
- No regression test is shown proving that non-propagatable transactions were previously delivered to ordinary propagation-facing listeners

## Severity Guidance

- Expected impact band: network_policy_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- The provided excerpt does not show the rest of on_new_pending_transaction, so actual enforcement using propagate_allowed is not visible
- No regression test is shown proving that non-propagatable transactions were previously delivered to ordinary propagation-facing listeners
