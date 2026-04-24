# Code-Shape Card

## Metadata

- ID: `sui-2024-08-20-sui-consensus-dab9bad618`
- Bug family: `resource_accounting_and_limits`
- Bug class: `consensus-resource-limit-hardening`

## Code Shape Summary

- The patch is security-relevant consensus resource-control work, but the provided evidence does not establish a concrete vulnerability or exploit path.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Enforce protocol-configured resource limits at the signed block verification boundary and return explicit verifier errors for limit violations.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
- The value is only advisory and is recomputed from canonical local consensus state before use.
