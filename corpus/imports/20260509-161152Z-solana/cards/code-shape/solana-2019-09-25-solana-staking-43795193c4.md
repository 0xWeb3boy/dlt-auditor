# Code-Shape Card

## Metadata

- ID: `solana-2019-09-25-solana-staking-43795193c4`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-hardening`

## Code Shape Summary

The patch is likely an access-control fix in Solana's vote API. The strongest supported change is that withdrawals now verify `vote_state.authorized_withdrawer` using a shared authorized-signer path, instead of only requiring the vote account itself to sign. Vote processing was also moved from inline authorized-voter signer matching to a shared helper, and the authorization API was generalized to handle voter or withdrawer roles.

## Search Motifs

- search for authorization hardening checks near staking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace generic or duplicated signer checks with centralized, role-aware authorization checks against authority fields stored in account state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
