# Root-Cause Card

## Metadata

- ID: `snarkos-2022-12-13-snarkos-p2p-networking-e8c8f3bd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-peer-address-resolution`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-peer-identity-resolution`

## Violated Invariant

- Invariant: Peer enforcement must resolve transient connection addresses to the canonical address used by the router peer table before disconnecting or penalizing.

## Trust Boundary

- Boundary: `peer-connection->router-peer-table`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: peer disconnect and enforcement target selection
- Attacker capability: trigger protocol-processing errors over an inbound connection; use a connection address that differs from tracked listener identity.
- Preconditions: router tracks peers by listener/canonical address; disconnect enforcement uses address key lookup.

## Impact Pattern

- Primary impact: wrong peer disconnect target.
- Secondary impact: misbehavior enforcement bypass or accidental disconnect.
- Severity guide: `low` for `peer-enforcement-correctness` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Peer enforcement must resolve transient connection addresses to the canonical address used by the router peer table before disconnecting or penalizing. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch corrects address resolution in snarkOS role routers before calling Router::disconnect after inbound protocol-processing errors. The evidence supports a P2P disconnect-targeting correctness fix across Validator, Prover, Client, and Beacon routers. It does not support the heuristic serialization/state-representation theory, and it does not establish an exploitable vulnerability or concrete denial-of-service impact. 1. In `node/src/validator/router.rs`, the patch replaces `async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::R...` with `async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io:...`. 2. In `node/src/prover/route
