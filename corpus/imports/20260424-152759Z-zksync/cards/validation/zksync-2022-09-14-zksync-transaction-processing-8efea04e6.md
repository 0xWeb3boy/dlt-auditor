# Validation Card

## Metadata

- ID: `zksync-2022-09-14-zksync-transaction-processing-8efea04e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `withdrawal-finalization-ordering`

## What Confirmed The Issue

- The old guard used the maximum processed withdrawal block.
- The patch scopes progress by block and compares withdrawal_tx_log_index.
- WithdrawalEvent now carries event.log_index into storage finalization.

## What Could Have Invalidated It

- Only one withdrawal event can exist per block by protocol design.
- Skipped events are reprocessed by a later independent reconciliation path before user impact.

## Severity Guidance

- Expected impact band: `fund_availability_state_integrity`
- Expected severity band: `medium_or_low`
- Rationale: Withdrawal finalization is sensitive and same-block event skipping can affect funds availability, but exploitability and theft are not proven.

## False-Positive Cautions

- If the protocol guarantees at most one relevant event per block, block-level idempotency may be sufficient.
- Parser assert-to-error changes are robustness signals, not proof of exploitability.
