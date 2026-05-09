# Code-Shape Card

## Metadata

- ID: `solana-2020-07-31-solana-staking-61d9d219f9`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`

## Code Shape Summary

The patch fixes a stake lockup role-confusion issue. Before the change, `Lockup::is_in_force` treated the lockup as not in force when the custodian public key appeared anywhere in a generic signer set. The commit message states this allowed a withdraw authority signature, and similarly fee-payer signing, to imply custodian authority when keys overlapped, causing lockup enforcement to be skipped. After the change, the lockup exemption is granted only whe...

## Search Motifs

- search for authorization role confusion checks near staking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace broad signer-set authorization checks with explicit role-qualified authority input for security-sensitive exemptions.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
