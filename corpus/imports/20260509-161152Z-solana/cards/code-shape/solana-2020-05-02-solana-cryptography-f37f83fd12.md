# Code-Shape Card

## Metadata

- ID: `solana-2020-05-02-solana-cryptography-f37f83fd12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-ordering`

## Code Shape Summary

The patch moves transaction sanitization and duplicate account-key rejection into `Accounts::lock_accounts`, before account lock key extraction. It removes the duplicate-key check from `load_tx_accounts` and removes the shown later `Bank::check_refs` sanitization path. This is a grounded validation-order cleanup or hardening change, but the supplied evidence does not prove a vulnerability, exploitability, consensus break, balance impact, replay issue, o...

## Search Motifs

- search for transaction sanitization ordering checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move malformed-transaction checks to the boundary that first consumes the transaction structure for account locking.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
