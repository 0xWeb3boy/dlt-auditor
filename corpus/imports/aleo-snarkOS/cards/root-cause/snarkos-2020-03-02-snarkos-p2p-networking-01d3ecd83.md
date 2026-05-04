# Root-Cause Card

## Metadata

- ID: `snarkos-2020-03-02-snarkos-p2p-networking-01d3ecd83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-panic-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `panic-safe-error-handling`

## Violated Invariant

- Invariant: Peer-controlled connection failures must be handled as ordinary protocol outcomes, not as panics or task-killing unwraps.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: network task lifecycle and peer disconnect handling
- Attacker capability: open a peer connection; abort handshake or close/read-fail the stream at protocol boundaries.
- Preconditions: node accepts inbound peer sessions; network errors or EOFs can propagate through the handshake/read path.

## Impact Pattern

- Primary impact: node availability degradation.
- Secondary impact: peer-task churn or noisy disconnect handling.
- Severity guide: `low` for `availability-hardening` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Peer-controlled connection failures must be handled as ordinary protocol outcomes, not as panics or task-killing unwraps. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: Commit 01d3ecd83 changes snarkOS server networking error handling so failed inbound handshakes are ignored instead of unwrapped, and peer read errors are logged and converted into a synthetic disconnect message. The evidence supports a robustness fix for a server EOF/thread panic, but does not establish a security vulnerability or a reliable remote denial-of-service impact. 1. In `network/src/server/server.rs`, the patch replaces `mut thread_sender: mpsc::Sender<(oneshot::Sender<Arc<Channel>>, MessageName, Vec<u8>,...` with `/// Spawns one thread per peer tcp connection to read messages`. 2. In `network/src/test_data/mod.rs`, the patch removes `/// Send a dummy message to the peer and make s
