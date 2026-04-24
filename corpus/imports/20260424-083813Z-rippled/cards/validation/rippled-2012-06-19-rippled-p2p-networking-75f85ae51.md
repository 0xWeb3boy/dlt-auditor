# Validation Card

## Metadata

- ID: `rippled-2012-06-19-rippled-p2p-networking-75f85ae51`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-gating`

## What Confirmed The Issue

- Evidence 1: Validation creation, trusted marking, signing, storage, and relay are now executed only when mValidating is true.
- Evidence 2: mValidating is enabled only when the configured validation seed is valid.

## What Could Have Invalidated It

- Compensating control 1: No Arthur bug report details are provided.
- Compensating control 2: No peer-side acceptance or rejection rules for validations/proposals are shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: consensus-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No Arthur bug report details are provided.
- Caution 2: No peer-side acceptance or rejection rules for validations/proposals are shown.
