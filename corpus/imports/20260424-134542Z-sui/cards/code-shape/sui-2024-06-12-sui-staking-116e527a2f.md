# Code-Shape Card

## Metadata

- ID: `sui-2024-06-12-sui-staking-116e527a2f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proxy-client-attribution-hardening`

## Code Shape Summary

- The patch is best described as proxy-aware traffic-control cleanup and hardening, not a confirmed vulnerability fix. The evidence supports that Sui traffic control previously had ambiguous client attribution around socket addresses, connection IP fields, and X-Forwarded-For handling in proxy deployments.

## Search Motifs

- input-validation enforced after parsing but before staking state mutation
- staking handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The staking sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Make the traffic-control client identity source explicit, pass an optional normalized client identity into checks, avoid acting on unsupported JSON-RPC forwarded-header data, and update policy accounting to use the normalized direct client field when available.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
