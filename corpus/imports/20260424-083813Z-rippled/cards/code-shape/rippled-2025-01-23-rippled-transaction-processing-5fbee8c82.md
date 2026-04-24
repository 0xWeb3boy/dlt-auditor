# Code-Shape Card

## Metadata

- ID: `rippled-2025-01-23-rippled-transaction-processing-5fbee8c82`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `validator-list-trust-policy-hardening`

## Code Shape Summary

- The patch adds and applies a configurable validator-list publisher threshold. The supplied evidence supports a UNL trust-policy hardening classification: trusted validator retention now checks publisher-list count against listThreshold_, and quorum readiness no longer depends... Reusable shape: check for trust-root-and-freshness-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact trust-root-and-freshness-validation check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an explicit configuration-backed trust threshold and enforce it at validator-list availability and trusted-key retention points.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the trust-root-and-freshness-validation gate runs before the state-changing branch.

## Patch Pattern

- Add an explicit configuration-backed trust threshold and enforce it at validator-list availability and trusted-key retention points.

## False Match Warnings

- No attacker path or exploit scenario is shown.
- No evidence of signature, manifest, or authentication bypass is shown.
