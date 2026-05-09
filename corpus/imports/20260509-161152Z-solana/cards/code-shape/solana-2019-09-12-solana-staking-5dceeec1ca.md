# Code-Shape Card

## Metadata

- ID: `solana-2019-09-12-solana-staking-5dceeec1ca`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`

## Code Shape Summary

The patch changes staking control paths to use `stake.check_authorized(...)` and `lockup.check_authorized(...)` with `other_signers`, but the supplied evidence does not establish that the previous behavior was an exploitable vulnerability. The commit also appears to add or generalize authorized-staker functionality, so this is best treated as potentially security-relevant authorization work rather than a confirmed vulnerability fix.

## Search Motifs

- search for improper authorization checks near staking entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace signer-presence checks with explicit state-derived authorization checks and thread additional signer context through the affected staking methods.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
