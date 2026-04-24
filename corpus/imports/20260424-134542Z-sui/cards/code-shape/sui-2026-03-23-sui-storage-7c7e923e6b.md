# Code-Shape Card

## Metadata

- ID: `sui-2026-03-23-sui-storage-7c7e923e6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-owner-resolution`

## Code Shape Summary

- The patch changes coin deny-list v2 owner extraction for written coin objects so that, under a new `use_coin_party_owner` protocol flag, it uses `object.owner.get_owner_address()` instead of always using `get_address_owner_address()`.

## Search Motifs

- authorization enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- object authority derived from request fields
- privileged mutation reachable before ownership check

## Typical Asymmetry

- The caller controls identifiers or objects that the sink treats as authority unless ownership is checked first.

## Patch Pattern

- Introduce a protocol-gated behavior change and use the party-owner-aware owner accessor only when the new protocol feature flag is enabled.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
