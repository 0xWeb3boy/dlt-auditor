# Code-Shape Card

## Metadata

- ID: `solana-2018-07-08-solana-cryptography-71f05cb23e`
- Bug family: `authz_and_role_gates`
- Bug class: `timestamp-source-authorization`

## Code Shape Summary

The patch fixes budget timestamp witness evaluation so future-payment conditions are checked against an explicit source public key before a locked budget can reduce to a payment. The evidence supports a contract-level authorization fix for timestamp sources, without proving a full exploit path or concrete loss.

## Search Motifs

- search for timestamp source authorization checks near cryptography entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where consensus, accounting, or authorization-sensitive state is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Propagate source identity into condition evaluation and require timestamp witnesses to match the authority encoded in the budget condition before performing the state transition.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
