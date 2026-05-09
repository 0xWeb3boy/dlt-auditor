# Root-Cause Card

## Metadata

- ID: `solana-2021-07-13-solana-cryptography-350baece21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-transaction-index`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

Transaction cost calculation assumed every instruction's `program_id_index` was valid for the message's `account_keys` array, even though the patched comment states the transaction may not be sanitized at that point.

## Impact Pattern

- Primary impact: availability-hardening
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch adds bounds checking before `CostModel::find_transaction_cost` indexes `transaction.message().account_keys` with `instruction.program_id_index`. Before the change, an out-of-range program_id_index could cause an invalid index access in the cost-model path. After the change, the function returns `CostModelError::InvalidTransaction`. Related `CostTracker` changes replace string errors with typed `CostModelError` variants but do not show a new re...
