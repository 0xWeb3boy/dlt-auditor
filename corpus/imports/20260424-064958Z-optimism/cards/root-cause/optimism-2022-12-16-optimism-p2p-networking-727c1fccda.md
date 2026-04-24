# Root-Cause Card

## Metadata

- ID: `optimism-2022-12-16-optimism-p2p-networking-727c1fccda`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `uncaught-panic-on-untrusted-input`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-and-failure-isolation`

## Violated Invariant

- Invariant: Peer-supplied gossip messages should be handled as validation failures, not allowed to escape the validator callback as unhandled panics.

## Trust Boundary

- Boundary: remote peer -> node networking validator

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: message acceptance, peer selection, or forkchoice update driven by network input

## Impact Pattern

- Primary impact: availability
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Peer-supplied gossip messages should be handled as validation failures, not allowed to escape the validator callback as unhandled panics. Similar bugs appear when p2p-message-handler code treats partially checked input as authoritative and lets it reach message acceptance, peer selection, or forkchoice update driven by network input. The reusable fix is to enforce resource-and-failure-isolation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
