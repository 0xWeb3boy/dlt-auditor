# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-02-12-go-ethereum-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-response-correlation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `request-response correlation`

## Violated Invariant

- Invariant: A network reply should only satisfy the pending request that generated the expected token or nonce for that exact exchange.

## Trust Boundary

- Boundary: Unauthenticated discovery datagrams -> local pending-request state.

## Attack Surface

- Entrypoint type: UDP discovery reply.
- Sensitive sink: Marking a ping as answered and updating discovery state for a peer.

## Impact Pattern

- Primary impact: Protocol-integrity weakening through response confusion.
- Secondary impact: Reduced spoofing or replay resistance in peer discovery.

## Short Reusable Lesson

- Identity checks are not enough for asynchronous protocols. If replies are accepted only because they came from the expected peer, stale or spoofed responses can satisfy the wrong pending request unless the code validates a request-derived token.
