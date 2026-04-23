# Validation Card

## Metadata

- ID: `nitro-2025-03-31-nitro-transaction-processing-475d442de`
- Bug family: `authz_and_role_gates`
- Bug class: `stale-authorization-state`

## What Confirmed The Issue

- Evidence 1: The patch is clearly hardening the express-lane admission path against stale or improperly validated submissions, but the provided evidence does not firmly establish a concrete vulnerability beyond correctness and fail-closed behavior.
- Evidence 2: Replace local/cached authorization lookups with tracker-backed validation at admission time and fail closed when the authoritative validator is unavailable.

## What Could Have Invalidated It

- Compensating control 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Compensating control 2: If the feature is disabled or only reachable in tests, classify similar cases as hardening or correctness only.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Caution 2: Do not claim fund loss or consensus breakage without evidence that the unchecked input reaches a state-changing sink.
