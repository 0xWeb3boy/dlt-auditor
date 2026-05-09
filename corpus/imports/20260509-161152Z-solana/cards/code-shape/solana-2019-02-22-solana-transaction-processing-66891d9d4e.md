# Code-Shape Card

## Metadata

- ID: `solana-2019-02-22-solana-transaction-processing-66891d9d4e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

The patch likely fixes an access-control flaw in Solana's native storage program by removing the separate global storage account userdata path. The strongest grounded evidence is the entrypoint change from two accounts to one signed account, removal of the `keyed_accounts[1]`/`storage_program::system_id()` path, and deletion of bank code that read storage state from that global account. The commit body also states that other accounts should not be able...

## Search Motifs

- search for access control checks near transaction-processing entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Remove the shared global userdata target and bind storage state access to the signed instruction account. Delete runtime/test assumptions that storage state lives under a separate global storage-system account.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
