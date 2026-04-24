# Validation Card

## Metadata

- ID: `rippled-2025-01-23-rippled-transaction-processing-1a341cb9c`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `validator-list-trust-threshold-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says the change improves UNL security.
- Evidence 2: Config parsing adds optional validator_list_threshold handling.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path is shown.
- Compensating control 2: No advisory, CVE, or vulnerability description is provided.

## Severity Guidance

- Expected impact band: security-impact: validator-trust-integrity, consensus-safety
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No concrete exploit path is shown.
- Caution 2: No advisory, CVE, or vulnerability description is provided.
