# Root-Cause Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-rpc-client-api-7cdc93d7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-penalty-for-invalid-consensus-version`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `peer-misbehavior-escalation`

## Violated Invariant

- Invariant: A peer that proves it is on an incompatible consensus version through block responses should not remain an eligible block source.

## Trust Boundary

- Boundary: `peer->block-sync-ingress`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: peer ban/disconnect state and block-sync source selection
- Attacker capability: send block responses with missing or mismatched consensus version; stay connected after validation failure.
- Preconditions: node validates consensus version during block response insertion; same peer can be selected again if not banned.

## Impact Pattern

- Primary impact: forked/outdated peers remain in sync pool.
- Secondary impact: repeated invalid response processing.
- Severity guide: `medium` for `peer-enforcement` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- A peer that proves it is on an incompatible consensus version through block responses should not remain an eligible block source. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch hardens snarkOS block-sync peer handling by banning peers whose block responses fail consensus-version validation in client and BFT ingress paths. The evidence supports a peer-enforcement hardening finding, not a proven invalid-block acceptance or consensus-safety vulnerability. 1. In `node/sync/src/block_sync.rs`, the patch replaces `return Err(InsertBlockResponseError::EmptyBlockResponse);` with `// Attempt to insert the block responses, and break if we encounter an error.`. 2. In `node/src/client/router.rs`, the patch replaces `false` with `// If the error indicates the peer missed an upgrade and forked, ban it.`. 3. In `node/bft/src/gateway.rs`, the patch adds `self.ip_ban_peer
