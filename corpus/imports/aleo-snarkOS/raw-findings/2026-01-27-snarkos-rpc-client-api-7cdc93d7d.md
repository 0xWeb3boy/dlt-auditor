---
case_id: case_20260127_7cdc93d7d
project: snarkos
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2026-01-27
source_refs:
  - git:7cdc93d7d016c35f5c93ffd81f4eeec32f5b3021
  - "node/sync/src/block_sync.rs:475"
  - "node/src/client/router.rs:223"
  - "node/bft/src/gateway.rs:656"
  - "node/src/client/router.rs:135"
bug_class: missing-peer-penalty-for-invalid-consensus-version
impact_type:
  - protocol-enforcement
  - peer-pool-integrity
confidence: high
tags:
  - blockchain-core
  - p2p
  - block-sync
  - consensus-version
  - peer-ban
  - protocol-enforcement
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens snarkOS block-sync peer handling by banning peers whose block responses fail consensus-version validation in client and BFT ingress paths. The evidence supports a peer-enforcement hardening finding, not a proven invalid-block acceptance or consensus-safety vulnerability.

## Observed Patch Facts

1. In `node/sync/src/block_sync.rs`, the patch replaces `return Err(InsertBlockResponseError::EmptyBlockResponse);` with `// Attempt to insert the block responses, and break if we encounter an error.`.

2. In `node/src/client/router.rs`, the patch replaces `false` with `// If the error indicates the peer missed an upgrade and forked, ban it.`.

3. In `node/bft/src/gateway.rs`, the patch adds `self.ip_ban_peer(peer_ip, Some(&err.to_string()));`.

4. In `node/src/client/router.rs`, the patch adds `//TODO(kaimast): set disconnect reason based on error`.

## Project Context

The changed code sits primarily in `node/sync/src`, `node/sync`, `node/src/client`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `node/src/client/mod.rs`, `node/bft/src/worker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `node/bft/src/sync/mod.rs`, `node/bft/src/helpers/channels.rs`. The strongest project-level identifiers around this patch are `peer_ip`, `InsertBlockResponseError::EmptyBlockResponse`, `InsertBlockResponseError`, and `error`. Nearby tests or test-like files include `node/bft/tests/components/worker.rs`, `node/bft/tests/common/test_peer.rs`.

## Before/After Behavior

Before the patch, the shown client router path logged insert_block_responses failures and returned false without banning peers for ConsensusVersionMismatch or NoConsensusVersion. The shown BFT gateway mismatch path logged and returned the error without banning. After the patch, the client router bans peers for ConsensusVersionMismatch and NoConsensusVersion, and the BFT gateway bans peers in the invalid block-response error arm. The block_sync change restructures error handling around a result block, but the provided evidence does not prove a separate root-cause bug there.

# Root Cause

Invalid or forked block-sync peers were rejected or errored in the shown paths, but peer penalties were not consistently applied for consensus-version validation failures. This allowed peers that sent missing or mismatched consensus-version data to remain available as future block sources.

## Walkthrough

1. A peer sends a block response with blocks and an optional latest_consensus_version.

2. BlockSync::insert_block_responses checks the response and can return InsertBlockResponseError variants including NoConsensusVersion and ConsensusVersionMismatch.

3. Before the patch, the client block_response path logged these insertion failures and returned false without banning the peer.

4. Before the patch, the shown BFT gateway ConsensusVersionMismatch path returned the error without banning the peer.

5. After the patch, the client router calls ip_ban_peer for ConsensusVersionMismatch and NoConsensusVersion.

6. After the patch, the BFT gateway calls ip_ban_peer in the invalid block-response error arm.

7. The fix changes peer-pool enforcement for rejected invalid responses; it does not show that invalid blocks were previously accepted.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| node/sync/src/block_sync.rs | 471 | validates block response height and expected consensus version, returning InsertBlockResponseError variants for empty, missing, or mismatched consensus-version cases |
| node/src/client/router.rs | 216 | client inbound block_response path calls block sync insertion and now bans peers on consensus-version mismatch or missing consensus version |
| node/bft/src/gateway.rs | 650 | BFT sync block response handling now bans peers whose inserted block response fails with empty, missing consensus version, or consensus-version mismatch errors |
| node/src/client/router.rs | 129 | general inbound message error path disconnects peers for protocol violation; only a TODO/comment changed here |

## Code Snippets

## Snippet 1

Context: `node/sync/src/block_sync.rs:475` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
latest_consensus_version: Option<ConsensusVersion>,
    ) -> Result<(), InsertBlockResponseError> {
        let Some(last_height) = blocks.as_slice().last().map(|b| b.height()) else {
            return Err(InsertBlockResponseError::EmptyBlockResponse);
        };

        let expected_consensus_version = N::CONSENSUS_VERSION(last_height)?;
```
After
```rust
latest_consensus_version: Option<ConsensusVersion>,
    ) -> Result<(), InsertBlockResponseError> {
        // Attempt to insert the block responses, and break if we encounter an error.
        let result = 'outer: {
            let Some(last_height) = blocks.as_slice().last().map(|b| b.height()) else {
                break 'outer Err(InsertBlockResponseError::EmptyBlockResponse);
            };
```

## Snippet 2

Context: `node/src/client/router.rs:223` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
if let Err(err) = self.sync.insert_block_responses(peer_ip, blocks, latest_consensus_version) {
            warn!("Failed to insert block response from '{peer_ip}' - {err}");
            false
        } else {
```
After
```rust
if let Err(err) = self.sync.insert_block_responses(peer_ip, blocks, latest_consensus_version) {
            warn!("Failed to insert block response from '{peer_ip}' - {err}");

            // If the error indicates the peer missed an upgrade and forked, ban it.
            if matches!(
                err,
                InsertBlockResponseError::ConsensusVersionMismatch { .. }
                    | InsertBlockResponseError::NoConsensusVersion
```

## Snippet 3

Context: `node/bft/src/gateway.rs:656` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
| Err(err @ InsertBlockResponseError::ConsensusVersionMismatch { .. }) => {
                            error!("Peer '{peer_ip}' sent an invalid block response - {err}");
                            Err(err.into())
                        }
```
After
```rust
| Err(err @ InsertBlockResponseError::ConsensusVersionMismatch { .. }) => {
                            error!("Peer '{peer_ip}' sent an invalid block response - {err}");
                            self.ip_ban_peer(peer_ip, Some(&err.to_string()));
                            Err(err.into())
                        }
```

## Snippet 4

Context: `node/src/client/router.rs:135` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
if let Err(error) = self.inbound(peer_addr, message).await {
            warn!("Failed to process inbound message from '{peer_addr}' - {error}");
            if let Some(peer_ip) = self.router().resolve_to_listener(peer_addr) {
                warn!("Disconnecting from '{peer_ip}' for protocol violation");
```
After
```rust
if let Err(error) = self.inbound(peer_addr, message).await {
            warn!("Failed to process inbound message from '{peer_addr}' - {error}");

            //TODO(kaimast): set disconnect reason based on error
            if let Some(peer_ip) = self.router().resolve_to_listener(peer_addr) {
                warn!("Disconnecting from '{peer_ip}' for protocol violation");
```

# Fix Pattern

Add peer penalties at block-response ingress points for consensus-version validation failures that were already represented as InsertBlockResponseError cases.

## How It Was Fixed

The patch adds ip_ban_peer calls in node/src/client/router.rs for ConsensusVersionMismatch and NoConsensusVersion from insert_block_responses, and adds an ip_ban_peer call in node/bft/src/gateway.rs for the invalid block-response error arm. The block_sync restructuring keeps errors available to callers, but the supported behavioral fix is the new banning logic.

# Why It Matters

1. Peers with missing or mismatched consensus-version data are removed as block sources.

2. Repeated invalid block responses become enforceable peer-pool events.

3. The change improves block-sync protocol hygiene.

4. The evidence does not prove invalid block acceptance or a finality break.

# Evidence Notes

Grounded evidence is limited to node/sync/src/block_sync.rs, node/src/client/router.rs, and node/bft/src/gateway.rs. The prior heuristic baseline about RPC serialization or canonical serialized state is unsupported and should be discarded. The patch does not show cryptographic verification changes, ledger acceptance of invalid blocks, or a demonstrated exploit path. Protocol security invariant: Peers that provide block responses with missing or mismatched consensus-version information should not remain eligible block-sync sources after those responses are rejected. Verification notes: The patch does not prove invalid-consensus-version blocks were accepted into the ledger before the change. The patch does not prove a consensus safety or finality break. The patch does not prove exploitability beyond repeated invalid block responses from non-banned peers. The patch does not show cryptographic verification changes. The patch does not establish that all malformed block responses are now banned, only the listed InsertBlockResponseError cases. Commit subject explicitly names banning peers with invalid consensus version. Diff shows new ip_ban_peer calls on consensus-version related InsertBlockResponseError cases. General router TODO comment is non-behavioral. Classified as security hardening rather than confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-peer-penalty-for-invalid-consensus-version`
Final impact type: `protocol-enforcement, peer-pool-integrity`
Final confidence: `high`
Final tags: `blockchain-core, p2p, block-sync, consensus-version, peer-ban, protocol-enforcement, security-hardening`

The supplied patch evidence supports retaining this as security hardening: peers whose block responses fail consensus-version validation are now banned in client and BFT ingress paths. The original finding correctly avoids claiming invalid block acceptance, but its subsystem, bug class, impact, and some tags are misleading because the evidence is about P2P/block-sync peer enforcement, not RPC serialization, signatures, queues, or client-view divergence.

## Security Evidence

1. Commit subject explicitly says peers with invalid consensus version are banned.
2. Client block_response now calls ip_ban_peer for ConsensusVersionMismatch and NoConsensusVersion from insert_block_responses.
3. BFT gateway now calls ip_ban_peer when a block response fails with consensus-version-related InsertBlockResponseError variants.
4. The changed behavior is in consensus/block-sync peer ingress paths, a security-sensitive blockchain networking area.

## Missing Evidence

1. No evidence that invalid-consensus-version blocks were previously accepted into ledger state.
2. No demonstrated exploit path, finality break, or consensus safety failure is shown.
3. No evidence that cryptographic verification or signature validation changed.
4. No tests or incident context prove concrete attacker impact beyond continued availability of invalid peers.

## Claim Boundaries

1. Validate only as peer-enforcement hardening for invalid or missing consensus-version block responses.
2. Do not classify as serialization/state-representation, RPC-client API, signature, or queue behavior.
3. Do not claim consensus compromise, invalid block acceptance, or client-view divergence from this patch alone.
4. The router TODO/comment-only change is not security evidence.
