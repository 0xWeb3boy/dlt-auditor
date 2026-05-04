# Root-Cause Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-rpc-client-api-45c9a26a5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-misbehavior-enforcement`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `peer-misbehavior-escalation`

## Violated Invariant

- Invariant: Inbound peers that send structurally invalid consensus-version block responses should be removed or penalized at the boundary that observed the misbehavior.

## Trust Boundary

- Boundary: `peer->block-sync-ingress`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: peer ban/disconnect state and block-sync source selection
- Attacker capability: send invalid block responses; omit or mismatch consensus-version data.
- Preconditions: block response validation detects structured errors; peer remains eligible unless enforcement maps the error to a penalty.

## Impact Pattern

- Primary impact: invalid peers remain eligible as sync sources.
- Secondary impact: repeated invalid response churn.
- Severity guide: `medium` for `peer-enforcement` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Inbound peers that send structurally invalid consensus-version block responses should be removed or penalized at the boundary that observed the misbehavior. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: Commit 45c9a26a5 hardens snarkOS block-sync handling by banning peers that trigger invalid consensus-version errors during block-response processing. The evidence supports a P2P enforcement hardening fix, not a demonstrated consensus bypass or invalid-block acceptance vulnerability. 1. In `node/sync/src/block_sync.rs`, the patch replaces `return Err(InsertBlockResponseError::EmptyBlockResponse);` with `// Attempt to insert the block responses, and break if we encounter an error.`. 2. In `node/src/client/router.rs`, the patch replaces `false` with `// If the error indicates the peer missed an upgrade and forked, ban it.`. 3. In `node/bft/src/gateway.rs`, the patch adds `self.ip_ban_peer(peer_
