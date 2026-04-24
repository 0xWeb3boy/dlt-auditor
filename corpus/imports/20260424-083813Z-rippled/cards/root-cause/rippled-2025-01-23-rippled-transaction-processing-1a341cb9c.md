# Root-Cause Card

## Metadata

- ID: `rippled-2025-01-23-rippled-transaction-processing-1a341cb9c`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `validator-list-trust-threshold-hardening`
- Confidence tier: `tier_a_confirmed`

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

- Primary impact: validator-trust-integrity, consensus-safety
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch adds an optional [validator_list_threshold] configuration and applies a threshold when maintaining trusted validator keys and deciding whether publisher-list availability is sufficient for achievable quorum behavior.
