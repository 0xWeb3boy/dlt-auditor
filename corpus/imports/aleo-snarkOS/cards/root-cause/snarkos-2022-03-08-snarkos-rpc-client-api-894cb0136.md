# Root-Cause Card

## Metadata

- ID: `snarkos-2022-03-08-snarkos-rpc-client-api-894cb0136`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-message-framing-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `framing-boundary-preservation`

## Violated Invariant

- Invariant: A framed-message parser must consume or drain every frame body consistently, even when the frame type is ignored or rejected.

## Trust Boundary

- Boundary: `peer->message-stream-parser`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: stream alignment and message deserialization
- Attacker capability: send framed network messages; choose unwanted or oversized payload bodies.
- Preconditions: parser reads multiple messages from one stream; ignored frames must still be drained to preserve alignment.

## Impact Pattern

- Primary impact: stream desynchronization or wasted deserialization.
- Secondary impact: crawler/synthetic-node availability degradation.
- Severity guide: `low` for `parser-hardening` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A framed-message parser must consume or drain every frame body consistently, even when the frame type is ignored or rejected. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The draft's RPC/state-representation thesis is unsupported. The grounded change is in snarkOS crawler and synthetic-node networking code: the crawler now uses a bounded expected-message buffer, reads frame metadata before full deserialization, and drains unwanted or oversized frame bodies. This may be security-relevant hardening against malformed or unnecessary peer input, but the provided evidence does not prove a vulnerability fix. 1. In `.crawler/src/crawler.rs`, the patch replaces `// FIXME: use the maximum message size allowed by the protocol or (better) use stream...` with `// This implementation is slightly low-level in order to discard unwanted messages wi...`. 2. In `.crawler/src/cr
