# Validation Card

## Metadata

- ID: `rippled-2018-10-08-rippled-rpc-client-api-7fe1d4b9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-site-redirect-retry-hardening`

## What Confirmed The Issue

- Evidence 1: ValidatorSite fetches validator-list site resources, a security-sensitive trust-data distribution path.
- Evidence 2: Resource construction validates parsed URLs and restricts schemes to http/https.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows an exploitable redirect vulnerability before the patch.
- Compensating control 2: No evidence shows attacker control over validator-site redirects in normal deployments.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: availability-hardening, bounded-network-fetch
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence shows an exploitable redirect vulnerability before the patch.
- Caution 2: No evidence shows attacker control over validator-site redirects in normal deployments.
