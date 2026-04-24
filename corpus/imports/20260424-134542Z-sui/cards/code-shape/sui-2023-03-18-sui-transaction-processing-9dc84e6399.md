# Code-Shape Card

## Metadata

- ID: `sui-2023-03-18-sui-transaction-processing-9dc84e6399`
- Bug family: `authz_and_role_gates`
- Bug class: `object-access-authentication-invariant`

## Code Shape Summary

- The patch adds debug-only invariant checking for authenticated object access after transaction execution and before effects are produced. This is security-relevant hardening, but the provided evidence does not establish a concrete production vulnerability or production enforcement change.

## Search Motifs

- authorization enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- object authority derived from request fields
- privileged mutation reachable before ownership check

## Typical Asymmetry

- The caller controls identifiers or objects that the sink treats as authority unless ownership is checked first.

## Patch Pattern

- Add a post-execution invariant assertion at a security-sensitive boundary, deriving authentication roots from transaction context and validating accessed objects against those roots.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
