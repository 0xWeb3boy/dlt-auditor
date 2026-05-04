# Root-Cause Card

## Metadata

- ID: `snarkos-2023-06-15-snarkos-rpc-client-api-5cc2764ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-deserialization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bounded-deserialization`

## Violated Invariant

- Invariant: Peer-controlled binary deserialization must enforce the same explicit size limit as the transport codec before allocating nested objects.

## Trust Boundary

- Boundary: `peer->message-deserializer`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: allocation and decode-time resource use
- Attacker capability: send encoded peer messages; choose collection lengths or payload structure within a frame.
- Preconditions: message deserializer uses length-prefixed collections; decode path can allocate before higher-level validation.

## Impact Pattern

- Primary impact: memory or CPU exhaustion during decode.
- Secondary impact: node availability degradation.
- Severity guide: `medium` for `availability` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Peer-controlled binary deserialization must enforce the same explicit size limit as the transport codec before allocating nested objects. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch hardens several snarkOS node message deserializers by replacing direct `bincode::deserialize_from` calls with configured bincode options that include `with_limit(MAXIMUM_MESSAGE_SIZE as u64)`. The evidence supports a resource-exhaustion hardening interpretation, but not a confirmed remotely exploitable vulnerability or any consensus, cryptographic, or replay flaw. 1. In `node/messages/src/challenge_request.rs`, the patch replaces `let (version, listener_port, node_type, address, nonce) = bincode::deserialize_from(&...` with `let options =`. 2. In `node/messages/src/ping.rs`, the patch replaces `let (version, node_type, block_locators) = bincode::deserialize_from(&mut reader)?;` wit
