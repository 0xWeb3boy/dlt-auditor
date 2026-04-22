# Validation Card

## Metadata

- ID: `oasis-core-2023-01-26-oasis-core-cryptography-8ffc81e94`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `insufficient-peer-identity-verification`

## What Confirmed The Issue

- Evidence 1: The patch threads the selected key manager node through the host RPC response, exposes remote-node identity from the session, and adds builder/client state used for remote identity verification. Per the commit message, Noise sessions then verify the selected member against consensus-derived trusted RAK material.
- Evidence 2: The source finding states the invariant explicitly: For explicit key manager member calls over Noise, the enclave must learn which node was selected and bind the authenticated session to that intended member using trusted identity material from consensus.

## What Could Have Invalidated It

- Compensating control 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Compensating control 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if trust roots, quote policy, and freshness evidence are atomically refreshed before each decision.
- Caution 2: Not a match if stale or changed session state is already invalidated on restart, reconfiguration, or peer change.
