# Validation Card

## Metadata

- ID: `rippled-2025-01-23-rippled-transaction-processing-5fbee8c82`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `validator-list-trust-policy-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says the change improves UNL security.
- Evidence 2: Config parsing adds a validator_list_threshold setting.

## What Could Have Invalidated It

- Compensating control 1: No attacker path or exploit scenario is shown.
- Compensating control 2: No evidence of signature, manifest, or authentication bypass is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: validator-trust-policy, unl-membership-integrity, quorum-readiness-policy
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No attacker path or exploit scenario is shown.
- Caution 2: No evidence of signature, manifest, or authentication bypass is shown.
