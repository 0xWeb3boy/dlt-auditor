# Validation Card

## Metadata

- ID: `oasis-core-2019-06-03-oasis-core-rpc-client-api-3f0716ecd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `non-production-credential-acceptance`

## What Confirmed The Issue

- Evidence 1: The fix introduced explicit registration of test public keys, a blacklist derived from that registration when test keys are disallowed, and an early blacklist check inside 'PublicKey.Verify'. A hardcoded keymanager test key is then registered so it is covered by the shared verification policy.
- Evidence 2: The source finding states the invariant explicitly: When test keys are disallowed, public keys explicitly designated as test-only must not pass the shared signature verification path, even if the signature is otherwise valid.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
