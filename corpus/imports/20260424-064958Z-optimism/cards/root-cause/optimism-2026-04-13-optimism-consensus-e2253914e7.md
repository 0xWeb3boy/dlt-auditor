# Root-Cause Card

## Metadata

- ID: `optimism-2026-04-13-optimism-consensus-e2253914e7`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-input-in-protocol-activation-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `freshness-and-fail-closed-validation`

## Violated Invariant

- Invariant: The Fjord hardfork gate for brotli-compressed channel data must be evaluated from trusted L1 origin context, not from batch payload timestamps. Nodes given the same origin must make the same accept/reject decision for brotli channels.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: consensus-deviation
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- The Fjord hardfork gate for brotli-compressed channel data must be evaluated from trusted L1 origin context, not from batch payload timestamps. Nodes given the same origin must make the same accept/reject decision for brotli channels. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce freshness-and-fail-closed-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
