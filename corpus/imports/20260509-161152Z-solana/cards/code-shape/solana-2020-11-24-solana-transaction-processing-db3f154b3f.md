# Code-Shape Card

## Metadata

- ID: `solana-2020-11-24-solana-transaction-processing-db3f154b3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-failed-transaction-state-persistence`

## Code Shape Summary

The supported finding is a likely Solana runtime state-integrity fix in durable nonce transaction handling. The strongest evidence is the change in `Accounts::collect_accounts_to_store` from storing any writable account to storing writable accounts only on successful execution, or on failed durable-nonce execution when the account is the nonce account or fee payer. Related fee-calculator changes appear to support consistent durable-nonce metadata handli...

## Search Motifs

- search for durable nonce failed transaction state persistence checks near transaction-processing entrypoints
- compare validation before and after the nonce-state-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Narrow failed-transaction persistence exceptions by making the durable nonce special case explicit: keep the ordinary success path, but on durable nonce instruction failure only allow nonce and fee-payer state to be stored.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
