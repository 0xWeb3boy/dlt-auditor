# Code-Shape Card

## Metadata

- ID: `solana-2020-05-02-solana-transaction-processing-fa254ff18f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-transaction-validation-ordering`

## Code Shape Summary

The patch moves transaction sanitization and duplicate-account-key rejection into `Accounts::lock_accounts` before lock key derivation, removes the duplicate-key rejection from later account loading, and removes a separate post-lock reference-check path in `Bank`. This is plausibly security relevant because it affects malformed transaction handling in runtime account locking, but the evidence does not prove a vulnerability or exploit path.

## Search Motifs

- search for malformed transaction validation ordering checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move malformed transaction validation to the earlier shared boundary that consumes transaction shape for lock derivation, and remove later duplicate validation paths whose ordering no longer matches the new flow.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
