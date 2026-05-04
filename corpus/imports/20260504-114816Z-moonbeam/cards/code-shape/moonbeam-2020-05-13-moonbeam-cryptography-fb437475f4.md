# Code-Shape Card

## Metadata

- ID: `moonbeam-2020-05-13-moonbeam-cryptography-fb437475f4`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`

## Code Shape Summary

- A dispatchable accepted a signed origin and raw caller-provided vectors, then wrote session-critical storage directly. The patch moved the state update behind unsigned payloads plus a signature-bearing validation boundary.

## Search Motifs

- ensure_signed(origin) followed by writes to validator/session snapshots
- dispatchable accepts raw Vec<AccountId> or snapshot data from caller
- offchain worker submit_signed path replaced by unsigned signed-payload validation

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Replace raw signed-origin persistence calls with unsigned signed-payload calls validated by the runtime before session storage is mutated.

## False Match Warnings

- Unsigned extrinsics are safe when validate_unsigned checks payload signature, freshness, and replay keys
- Signed administrative-only calls may be acceptable if governance/root is the only origin
- Pure telemetry snapshots with no consensus or reward effect are lower severity
