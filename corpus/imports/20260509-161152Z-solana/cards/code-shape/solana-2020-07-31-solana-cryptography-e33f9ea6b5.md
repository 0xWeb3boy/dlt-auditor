# Code-Shape Card

## Metadata

- ID: `solana-2020-07-31-solana-cryptography-e33f9ea6b5`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`

## Code Shape Summary

The patch fixes a stake lockup bypass caused by treating custodian authorization as membership in a generic signer set. The strongest grounded claim is authority-role confusion in stake withdrawal lockup enforcement, not replay, cryptography, network, or validator repair logic.

## Search Motifs

- search for authorization role confusion checks near cryptography entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace generic signer-set checks for privileged role bypasses with explicit account-role binding, so each authorization decision is tied to the specific role account being evaluated.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
