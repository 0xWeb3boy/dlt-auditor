# Validation Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-a02e1e95f`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `improper-trust-verification-gating`

## What Confirmed The Issue

- Evidence 1: The executor now starts runtime trust sync during runtime startup, requires 'runtimeTrustSynced' before advertising availability, and cancels outstanding sync work when the runtime stops or fails. Mock runtime support was extended so the new consensus-sync request path can succeed in non-production coverage.
- Evidence 2: The source finding states the invariant explicitly: When a runtime is configured with a trust root, executor availability/registration should wait until runtime trust sync has completed; generic runtime readiness and last-round availability alone are not sufficient.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
