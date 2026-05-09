# Code-Shape Card

## Metadata

- ID: `solana-2019-03-01-solana-staking-db825b6e26`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-check`

## Code Shape Summary

The patch moves a signer check from a blanket native vote entrypoint guard into sdk/src/vote_program.rs::process_vote, immediately before VoteState is deserialized, mutated, and serialized. This is security-relevant authorization hardening, but the provided evidence does not establish that unsigned votes were accepted through the normal runtime path before the patch, because the old entrypoint already rejected unsigned keyed_accounts[0] before dispatch.

## Search Motifs

- search for missing signature check checks near staking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Place authorization checks directly in the state-mutating function that requires them, while avoiding overbroad entrypoint assumptions for unrelated instruction variants.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
