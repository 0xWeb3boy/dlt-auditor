# Root-Cause Card

## Metadata

- ID: `bor-2015-01-19-bor-p2p-networking-e252c634c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `public-key-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network peer authenticity and protocol state validation`

## Violated Invariant

- Invariant: A node must authenticate, correlate, and validate peer-controlled protocol data before using it to advance handshake, sync, or peer-state decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: availability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The only grounded issue shown is that the responder helper previously relied on a pre-parsed public key from its caller instead of decoding and rejecting invalid key bytes at the point of use. The provided evidence does not establish whether that was an exploitable security flaw or simply a correctness problem during handshake integration.
