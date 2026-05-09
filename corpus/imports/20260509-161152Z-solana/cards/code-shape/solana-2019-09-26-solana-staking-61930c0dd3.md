# Code-Shape Card

## Metadata

- ID: `solana-2019-09-26-solana-staking-61930c0dd3`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-hardening`

## Code Shape Summary

The evidence supports a likely authorization fix in Solana vote/stake authority handling. The strongest supported change is in vote withdrawal: the pre-patch path only required the vote account itself to be a signer, while the patched path loads VoteState and verifies vote_state.authorized_withdrawer against the vote account and other signers. Vote processing is also moved to shared verification of vote_state.authorized_voter. The stake changes appear t...

## Search Motifs

- search for authorization check hardening checks near staking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace account-key or field-specific signer checks with validation against role-specific authority stored in account state, and thread additional signer accounts through the affected instruction paths.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
