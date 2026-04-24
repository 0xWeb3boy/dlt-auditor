# Code-Shape Card

## Metadata

- ID: `sui-2025-09-10-sui-consensus-606de5ea65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-dos-hardening`

## Code Shape Summary

- The supported finding is a DoS-oriented hardening change for Sui's Mysticeti fast path transaction submission flow. The patch adds submitted-transaction accounting and client attribution so repeated submissions of the same user transaction digest can be counted after the transaction appears in consensus output and excess.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Add bounded resource accounting at the point where repeated resource use becomes observable, propagate client attribution from ingress through the relevant submission path, and connect excess usage to an existing throttling mechanism.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
- The value is only advisory and is recomputed from canonical local consensus state before use.
