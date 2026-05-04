# Root-Cause Card

## Metadata

- ID: `snarkos-2021-04-13-snarkos-p2p-networking-b2baa32e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-block-sync-state-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `sync-state-correlation`

## Violated Invariant

- Invariant: A block-sync payload should be processed only if it matches the node state that says this peer is the expected sync source.

## Trust Boundary

- Boundary: `peer->block-sync-state-machine`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: consensus sync processing and peer-book state
- Attacker capability: send Sync payloads or influence sync peer selection; race or reuse stale sync state.
- Preconditions: node tracks expected sync source/state; unexpected sync payload can reach consensus.received_sync.

## Impact Pattern

- Primary impact: unexpected sync payload processing.
- Secondary impact: stale peer bookkeeping or inefficient sync behavior.
- Severity guide: `medium` for `sync-integrity-hardening` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A block-sync payload should be processed only if it matches the node state that says this peer is the expected sync source. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch hardens snarkOS block-sync state handling, but the supplied evidence does not establish a concrete vulnerability. The strongest grounded change is that Payload::Sync previously called peer_book.expecting_sync_blocks(...) but ignored its boolean result, then still invoked consensus.received_sync(...). After the patch, consensus sync handling is gated on that boolean. The patch also clears outstanding per-peer sync counters before registering a new sync attempt and moves peer-height eligibility into consensus.should_sync_blocks(peer_block_height). 1. In `network/src/inbound/inbound.rs`, the patch replaces `self.peer_book.read().expecting_sync_blocks(source.unwrap(), sync.len());` wit
