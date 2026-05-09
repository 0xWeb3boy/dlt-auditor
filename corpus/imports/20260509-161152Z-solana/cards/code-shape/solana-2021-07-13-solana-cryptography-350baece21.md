# Code-Shape Card

## Metadata

- ID: `solana-2021-07-13-solana-cryptography-350baece21`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-transaction-index`

## Code Shape Summary

The patch adds bounds checking before `CostModel::find_transaction_cost` indexes `transaction.message().account_keys` with `instruction.program_id_index`. Before the change, an out-of-range program_id_index could cause an invalid index access in the cost-model path. After the change, the function returns `CostModelError::InvalidTransaction`. Related `CostTracker` changes replace string errors with typed `CostModelError` variants but do not show a new re...

## Search Motifs

- search for panic on invalid transaction index checks near cryptography entrypoints
- compare validation before and after the resource-accounting-and-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for allocation, serialization, fanout, or scheduling before quota checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate transaction message indexes before dereferencing message arrays, and convert panic-prone assumptions into typed error returns.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
