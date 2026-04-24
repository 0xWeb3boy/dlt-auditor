# Root-Cause Card

## Metadata

- ID: `rippled-2025-01-23-rippled-transaction-processing-5fbee8c82`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `validator-list-trust-policy-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-and-freshness-validation`

## Violated Invariant

- Invariant: Externally supplied trust material must be fetched, redirected, cached, and accepted only under the configured trust roots and transport policy.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: validator-trust-policy, unl-membership-integrity, quorum-readiness-policy
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch adds and applies a configurable validator-list publisher threshold. The supplied evidence supports a UNL trust-policy hardening classification: trusted validator retention now checks publisher-list count against listThreshold_, and quorum readiness no longer depends on every publisher being available but on sufficient publisher-list availability.
