# Code-Shape Card

## Metadata

- ID: `sui-2024-07-16-sui-core-logic-4ba06ed746`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-query-limit-hardening`

## Code Shape Summary

- The patch rewrites Sui GraphQL query limit accounting and tightens several limit-checking behaviors. The evidence supports a correctness and hardening change in a resource-limit guard, but it does not establish a concrete vulnerability, exploit path, or externally demonstrated denial of service.

## Search Motifs

- resource-accounting enforced after parsing but before core-logic state mutation
- core-logic handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Reimplement resource-limit accounting with explicit budgets, refine GraphQL introspection exemption logic, and improve traversal of GraphQL connection and fragment structures.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
