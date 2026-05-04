# Validation Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-transaction-processing-bb0aa99bf1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`

## What Confirmed The Issue

- Evidence 1: In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `StacksChainState::process_transaction_token_transfer(clarity_tx,tx, origin_account)?;` with `// this only works for standard authorizations`.
- Evidence 2: In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `let amount_sent = asset_map.get_stx(&origin_account.principal).unwrap_or(0);` with `let amount_sent = asset_map.get_stx(&account.principal).unwrap_or(0);`.

## What Could Have Invalidated It

- Compensating control 1: The constructor may be used only with trusted constants.
- Compensating control 2: The changed path may improve diagnostics without changing acceptance behavior.

## Severity Guidance

- Expected impact band: `authorization_or_message_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The constructor may be used only with trusted constants.
- Caution 2: The changed path may improve diagnostics without changing acceptance behavior.
