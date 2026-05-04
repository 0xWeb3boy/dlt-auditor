# Root-Cause Card

## Metadata

- ID: `snarkos-2023-09-22-snarkos-rpc-client-api-4d4ed026e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-request-response-correlation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `request-response-correlation`

## Violated Invariant

- Invariant: A response that can update discovery state or initiate connections must match an outstanding request for the same peer.

## Trust Boundary

- Boundary: `peer->validator-discovery-state`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: validator discovery connection attempts
- Attacker capability: send ValidatorsResponse messages; choose validator list contents or send unsolicited responses.
- Preconditions: node accepts validator discovery responses from peers; response can drive connection attempts or discovery state.

## Impact Pattern

- Primary impact: unsolicited discovery response processing.
- Secondary impact: connection churn or peer graph manipulation.
- Severity guide: `medium` for `discovery-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A response that can update discovery state or initiate connections must match an outstanding request for the same peer. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch adds a peer-specific outstanding-request guard before Narwhal processes a ValidatorsResponse. The provided evidence supports a validator-discovery hardening change: before the patch, the shown response path enforced only a validator-count limit before proceeding toward connection attempts; after the patch, unmatched responses are rejected and matched responses decrement request-tracking state. 1. In `node/narwhal/src/gateway.rs`, the patch replaces `// Attempt to connect to any validators that are not already connected.` with `// Ensure the cache contains a validators request for this peer.`. 2. In `node/narwhal/src/helpers/cache.rs`, the patch adds `/// Increments the key's counte
