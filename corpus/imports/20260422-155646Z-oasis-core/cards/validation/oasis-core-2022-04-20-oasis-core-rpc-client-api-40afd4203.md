# Validation Card

## Metadata

- ID: `oasis-core-2022-04-20-oasis-core-rpc-client-api-40afd4203`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `trust-root-verification`

## What Confirmed The Issue

- Evidence 1: The change introduces 'runtimeTrustSynced' into the availability condition, resets that state on runtime start, initiates trust synchronization, and cancels outstanding sync work on stop or failure. Supporting mock code was updated to accept 'RuntimeConsensusSyncRequest'.
- Evidence 2: The source finding states the invariant explicitly: If a runtime is configured with a trust root, the executor should not register as available until trust synchronization has completed.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
