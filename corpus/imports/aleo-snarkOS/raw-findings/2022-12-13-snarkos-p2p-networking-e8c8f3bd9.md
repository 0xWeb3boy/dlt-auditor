---
case_id: case_20221213_e8c8f3bd9
project: snarkos
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: p2p-networking
source_quality: medium
date: 2022-12-13
source_refs:
  - git:e8c8f3bd9cbb10d86b0be0d06bdf009252f3af01
  - "node/src/validator/router.rs:106"
  - "node/src/prover/router.rs:97"
  - "node/src/client/router.rs:90"
  - "node/src/beacon/router.rs:105"
bug_class: incorrect-peer-address-resolution
impact_type:
  - p2p-enforcement-bypass
  - malicious-peer-retention
confidence: medium
tags:
  - p2p-networking
  - protocol-violation-handling
  - disconnect-enforcement
  - peer-address-resolution
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects address resolution in snarkOS role routers before calling Router::disconnect after inbound protocol-processing errors. The evidence supports a P2P disconnect-targeting correctness fix across Validator, Prover, Client, and Beacon routers. It does not support the heuristic serialization/state-representation theory, and it does not establish an exploitable vulnerability or concrete denial-of-service impact.

## Observed Patch Facts

1. In `node/src/validator/router.rs`, the patch replaces `async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::R...` with `async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io:...`.

2. In `node/src/prover/router.rs`, the patch replaces `async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::R...` with `async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io:...`.

3. In `node/src/client/router.rs`, the patch replaces `async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::R...` with `async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io:...`.

4. In `node/src/beacon/router.rs`, the patch replaces `async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::R...` with `async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io:...`.

## Project Context

The changed code sits primarily in `node/src/validator`, `node/src`, `node/src/prover`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `node/src/validator/mod.rs`, `node/src/prover/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `node/src/validator/mod.rs`, `node/src/prover/mod.rs`. The strongest project-level identifiers around this patch are `peer_ip`, `Self::Message`, `io::Result`, and `Message::Disconnect`.

## Before/After Behavior

Before the patch, process_message used the SocketAddr passed into the handler directly for inbound processing, ProtocolViolation disconnect sending, and Router::disconnect. After the patch, the same observed peer_addr is still passed to inbound(...), but on inbound error the code first calls router().resolve_to_listener(&peer_addr); only when that returns Some(peer_ip) does it send Message::Disconnect(ProtocolViolation) and call router().disconnect(peer_ip).

# Root Cause

The code treated the process_message SocketAddr as the address identity suitable for router disconnect enforcement. The patch implies that this observed connection address can differ from the listener address tracked by the router, so direct use could target disconnect handling at the wrong address representation.

## Walkthrough

1. A message is received by a role-specific Reading::process_message implementation.

2. The handler calls inbound(peer_addr, message).

3. If inbound returns an error, the code treats the peer as having violated the protocol.

4. Before the patch, the error path sent Message::Disconnect and called Router::disconnect using the original process_message address.

5. After the patch, the error path resolves that address through router().resolve_to_listener(&peer_addr).

6. If resolution succeeds, the resolved listener address is used for the disconnect message and router removal.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| node/src/validator/router.rs | 106 | Validator inbound message handler resolves peer_addr to listener address before ProtocolViolation disconnect and router removal. |
| node/src/prover/router.rs | 97 | Prover inbound message handler resolves peer_addr to listener address before ProtocolViolation disconnect and router removal. |
| node/src/client/router.rs | 90 | Client inbound message handler resolves peer_addr to listener address before ProtocolViolation disconnect and router removal. |
| node/src/beacon/router.rs | 105 | Beacon inbound message handler resolves peer_addr to listener address before ProtocolViolation disconnect and router removal. |

## Code Snippets

## Snippet 1

Context: `node/src/validator/router.rs:106` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_ip, message).await {
            warn!("Disconnecting from '{peer_ip}' - {error}");
            self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
            // Disconnect from this peer.
```
After
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_addr, message).await {
            if let Some(peer_ip) = self.router().resolve_to_listener(&peer_addr) {
                warn!("Disconnecting from '{peer_ip}' - {error}");
                self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
```

## Snippet 2

Context: `node/src/prover/router.rs:97` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_ip, message).await {
            warn!("Disconnecting from '{peer_ip}' - {error}");
            self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
            // Disconnect from this peer.
```
After
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_addr, message).await {
            if let Some(peer_ip) = self.router().resolve_to_listener(&peer_addr) {
                warn!("Disconnecting from '{peer_addr}' - {error}");
                self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
```

## Snippet 3

Context: `node/src/client/router.rs:90` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_ip, message).await {
            warn!("Disconnecting from '{peer_ip}' - {error}");
            self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
            // Disconnect from this peer.
```
After
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_addr, message).await {
            if let Some(peer_ip) = self.router().resolve_to_listener(&peer_addr) {
                warn!("Disconnecting from '{peer_ip}' - {error}");
                self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
```

## Snippet 4

Context: `node/src/beacon/router.rs:105` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_ip: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_ip, message).await {
            warn!("Disconnecting from '{peer_ip}' - {error}");
            self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
            // Disconnect from this peer.
```
After
```rust
/// Processes a message received from the network.
    async fn process_message(&self, peer_addr: SocketAddr, message: Self::Message) -> io::Result<()> {
        // Process the message. Disconnect if the peer violated the protocol.
        if let Err(error) = self.inbound(peer_addr, message).await {
            if let Some(peer_ip) = self.router().resolve_to_listener(&peer_addr) {
                warn!("Disconnecting from '{peer_ip}' - {error}");
                self.send(peer_ip, Message::Disconnect(DisconnectReason::ProtocolViolation.into()));
```

# Fix Pattern

Resolve the observed peer connection address to the router's tracked listener address before invoking disconnect enforcement.

## How It Was Fixed

Validator, Prover, Client, and Beacon router process_message implementations were updated to rename the handler argument from peer_ip to peer_addr, retain it for inbound processing, then call resolve_to_listener before sending ProtocolViolation disconnects and calling Router::disconnect.

# Why It Matters

1. Keeps disconnect handling aligned with the router's tracked peer address.

2. Avoids relying on a possibly non-canonical connection SocketAddr for peer removal.

3. The patch touches protocol-violation handling, so it may be security relevant.

4. The supplied evidence does not prove exploitability or concrete security impact.

# Evidence Notes

Primary evidence is the changed process_message logic in node/src/validator/router.rs, node/src/prover/router.rs, node/src/client/router.rs, and node/src/beacon/router.rs. The changed lines show resolve_to_listener added before Message::Disconnect and Router::disconnect. The evidence does not show attacker control over address mapping, whether failed resolution has fallback behavior, or a demonstrated impact such as persistent malicious peer access or denial of service. The supplied diff does not support claims about canonical serialized state transfer. Protocol security invariant: When handling an inbound protocol violation, disconnect logic should address the peer identity tracked by the router. The patch shows the observed connection address being resolved to the router listener address before sending a ProtocolViolation disconnect and calling Router::disconnect, but the evidence does not establish a concrete security impact if this resolution is skipped. Verification notes: The patch does not prove consensus, ledger, cryptographic, or economic impact. The patch does not show that an attacker can forge or control the address mapping. The patch does not prove a denial-of-service condition; it only shows incorrect disconnect targeting could occur. The patch does not support the heuristic claim about canonical serialized state transfer. The evidence does not show whether failed resolve_to_listener leaves any additional fallback behavior elsewhere. Downgraded mapper confidence from high to medium because impact is inferred from disconnect-path semantics. Downgraded security_verdict from likely to unclear because the vulnerability thesis is not established by the provided evidence. Set keep_in_security_corpus to false under the instruction for security-relevant but unproven fixes. Rejected the heuristic serialization/state-representation classification as unsupported. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-peer-address-resolution`
Final impact type: `p2p-enforcement-bypass, malicious-peer-retention`
Final confidence: `medium`
Final tags: `p2p-networking, protocol-violation-handling, disconnect-enforcement, peer-address-resolution, security-hardening`

The patch does not prove a concrete exploitable vulnerability, but it does clearly tighten security-sensitive P2P enforcement: peers that trigger inbound protocol-processing errors are supposed to receive a ProtocolViolation disconnect and be removed from the router, and the fix resolves the observed connection address to the router-tracked listener address before enforcing that disconnect. The original serialization/state-representation classification is unsupported; the defensible corpus entry is narrower security hardening around correct disconnect targeting.

## Security Evidence

1. Changed protocol-violation error paths in Validator, Prover, Client, and Beacon routers.
2. Before the patch, Message::Disconnect and Router::disconnect used the raw process_message SocketAddr directly.
3. After the patch, the code resolves peer_addr with router().resolve_to_listener before sending ProtocolViolation disconnects and removing the peer.
4. The affected path handles network messages and explicitly disconnects peers that violated the protocol.

## Missing Evidence

1. No proof that an attacker could intentionally exploit the address mismatch.
2. No demonstrated denial-of-service, consensus, ledger, or economic impact.
3. No evidence showing how often resolve_to_listener fails or what fallback behavior exists elsewhere.
4. No security advisory, vulnerability identifier, or exploit regression test is provided.

## Claim Boundaries

1. Keep as security-hardening, not as a confirmed security-fix.
2. Do not claim serialization, canonical state encoding, consensus divergence, or client-view divergence.
3. Do not claim proven DoS or persistent malicious peer access from the patch alone.
4. The supported claim is limited to correcting P2P protocol-violation disconnect targeting across role routers.
