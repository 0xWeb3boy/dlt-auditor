# Root-Cause Card

## Metadata

- ID: `snarkos-2022-10-28-snarkos-p2p-networking-63f6f9bc2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-protocol-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `envelope-payload-consistency`

## Violated Invariant

- Invariant: When a protocol envelope repeats identifiers also derivable from the payload, the receiver must verify they match before updating routing state.

## Trust Boundary

- Boundary: `peer->router-object-cache`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: unconfirmed transaction/solution routing and propagation state
- Attacker capability: send unconfirmed transaction or solution messages; choose envelope metadata inconsistent with payload identifiers.
- Preconditions: message contains redundant metadata and payload identifiers; router updates caches or forwards object based on either representation.

## Impact Pattern

- Primary impact: incorrect propagation metadata.
- Secondary impact: cache poisoning or object misrouting hardening.
- Severity guide: `medium` for `mempool-routing-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- When a protocol envelope repeats identifiers also derivable from the payload, the receiver must verify they match before updating routing state. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch adds inbound consistency checks for UnconfirmedTransaction and UnconfirmedSolution messages and changes outbound routing metadata lookup to use stored envelope fields instead of deriving identifiers from Data::Object payloads. The change is protocol-validation hardening, but the supplied evidence does not establish a concrete vulnerability or attacker-impact path. 1. In `node/router/src/outbound.rs`, the patch replaces `let transaction_id = if let Data::Object(transaction) = &message.transaction {` with `let transaction_id = message.transaction_id;`. 2. In `node/router/src/outbound.rs`, the patch replaces `let puzzle_commitment = if let Data::Object(solution) = &message.solution {`
