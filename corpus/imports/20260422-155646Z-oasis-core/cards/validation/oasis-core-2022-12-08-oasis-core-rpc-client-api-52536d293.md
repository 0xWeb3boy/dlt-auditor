# Validation Card

## Metadata

- ID: `oasis-core-2022-12-08-oasis-core-rpc-client-api-52536d293`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `quote-policy-synchronization`

## What Confirmed The Issue

- Evidence 1: The fix introduces quote-policy update delivery into the runtime, adds epoch-based refresh logic because quote policy may change on redeploy, and adds a runtime-side handler to receive the new policy state. This makes the quote policy available to the runtime along the same trust path as other key-manager policy updates.
- Evidence 2: The source finding states the invariant explicitly: If enclave RPC quote verification depends on the key manager's consensus-published SGX quote policy, the runtime must receive and refresh that policy when it changes so verification does not rely on stale local state.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
