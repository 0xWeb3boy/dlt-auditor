# Root-Cause Card

## Metadata

- ID: `fuel-core-2023-10-25-fuel-core-rpc-client-api-ba21e247d3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `p2p-reserved-peer-reputation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Transient validation races from trusted or reserved propagation paths must not be scored as peer misbehavior unless the peer actually violated the protocol.

## Trust Boundary

- Boundary: `reserved-peer->node-reputation`
- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `peer reputation scoring and reserved-peer connectivity`

## Attack Surface

- Cause or relay transactions that can become invalid because local chain state races ahead.
- Use normal gossip paths that affect peer scoring.

## Exploit Preconditions

- Reserved peers or sentries are scored with the same rejection semantics as untrusted peers.
- A benign race can produce a hard reject instead of a neutral ignore.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `peer-partition-risk`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Separate payload validity from peer blame when trusted propagation paths can encounter state races outside the peer control.
