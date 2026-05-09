---
case_id: case_20190308_c8c85ff93b
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
confidence: medium
source_quality: high
date: 2019-03-08
source_refs:
  - git:c8c85ff93b9508f67fdfe891ee8c26990baef833
  - "core/src/cluster_info.rs:778"
  - "core/src/cluster_info.rs:1504"
  - "core/src/cluster_info.rs:177"
  - "core/src/cluster_info.rs:819"
bug_class: gossip-signature-integrity
impact_type:
  - integrity
tags:
  - blockchain-core
  - p2p-networking
  - gossip
  - signature
  - identity-binding
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Solana gossip initialization so the local self ContactInfo is inserted through a dedicated insert_self path instead of the generic insert_info path. The new path checks that node_info.id matches the local node id, signs the ContactInfo with the local keypair, and only then inserts it into CRDS. This supports a likely security fix for preventing incorrectly signed self gossip records, though the provided evidence does not establish remote exploitability or downstream consensus impact.

## Observed Patch Facts

1. In `core/src/cluster_info.rs`, the patch replaces `fn new_pull_requests(&mut self, stakes: &HashMap<Pubkey, u64>) -> Vec<(SocketAddr, Pr...` with `// If the network entrypoint hasn't been discovered yet, add it to the crds table`.

2. In `core/src/cluster_info.rs`, the patch replaces `fn window_index_request() {` with `fn test_insert_self() {`.

3. In `core/src/cluster_info.rs`, the patch replaces `me.insert_info(node_info);` with `entrypoint: None,`.

4. In `core/src/cluster_info.rs`, the patch replaces `.map(|(peer, filter, gossip, self_info)| {` with `if pr.is_empty() {`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `core/src/gossip_service.rs`, `core/src/crds_gossip_pull.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/replicator.rs`, `core/src/gossip_service.rs`. The strongest project-level identifiers around this patch are `CrdsValueLabel::ContactInfo`, `NodeInfo::new_localhost`, `Keypair::new`, and `entrypoint`.

## Before/After Behavior

Before the patch, ClusterInfo::new inserted the local node_info through generic insert_info after setting the gossip self id. The provided evidence does not show that this generic path enforced a self-identity match at that boundary. After the patch, ClusterInfo::new calls insert_self, which requires self.id() == node_info.id, signs the ContactInfo with self.keypair, and inserts only matching self records. A new test confirms that the self label is present and that a different NodeInfo cannot be inserted through insert_self. The patch also adds an entrypoint pull fallback that uses the local self ContactInfo when no normal pull targets are available.

# Root Cause

The self ContactInfo initialization path used a generic insertion function rather than a dedicated self-record path with an explicit identity match check and local signing step. Based on the shown diff and commit subject, this could allow propagation of self gossip data whose signature did not correspond cleanly to the advertised identity.

## Walkthrough

1. ClusterInfo::new records the local id with me.gossip.set_self(id).

2. The old initialization then called me.insert_info(node_info).

3. The patch replaces that call with me.insert_self(node_info).

4. insert_self checks whether self.id() equals node_info.id before constructing a CrdsValue::ContactInfo.

5. For matching identities, insert_self signs the ContactInfo with self.keypair and inserts it into self.gossip.crds.

6. For mismatched identities, insert_self does not insert the record.

7. The added test verifies both successful self insertion and rejection of a different NodeInfo through the self path.

8. new_pull_requests now falls back to add_entrypoint when no regular pull targets exist, using the local self ContactInfo already stored in CRDS.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/cluster_info.rs | 174 | ClusterInfo initialization now uses insert_self for the local node record instead of generic insert_info. |
| core/src/cluster_info.rs | 177 | insert_self enforces the local identity match, signs ContactInfo with the local keypair, and inserts only that signed value. |
| core/src/cluster_info.rs | 778 | entrypoint pull fallback uses the local self ContactInfo when bootstrapping gossip discovery. |
| core/src/cluster_info.rs | 801 | new_pull_requests falls back to add_entrypoint only when ordinary gossip pull targets are unavailable. |
| core/src/cluster_info.rs | 1504 | test coverage asserts self insertion exists and mismatched identity insertion is rejected. |

## Code Snippets

## Snippet 1

Context: `core/src/cluster_info.rs:778` (changes signature or replay validation logic)

Before
```rust
Ok((addr, out))
    }

    fn new_pull_requests(&mut self, stakes: &HashMap<Pubkey, u64>) -> Vec<(SocketAddr, Protocol)> {
```
After
```rust
Ok((addr, out))
    }
    // If the network entrypoint hasn't been discovered yet, add it to the crds table
    fn add_entrypoint(&mut self, pulls: &mut Vec<(Pubkey, Bloom<Hash>, SocketAddr, CrdsValue)>) {
        match &self.entrypoint {
            Some(entrypoint) => {
                let self_info = self
                    .gossip
```

## Snippet 2

Context: `core/src/cluster_info.rs:1504` (changes the branch that decides whether execution stops or continues)

Before
```rust
}
    #[test]
    fn window_index_request() {
        let me = NodeInfo::new_localhost(Keypair::new().pubkey(), timestamp());
```
After
```rust
}
    #[test]
    fn test_insert_self() {
        let d = NodeInfo::new_localhost(Keypair::new().pubkey(), timestamp());
        let mut cluster_info = ClusterInfo::new_with_invalid_keypair(d.clone());
        let entry_label = CrdsValueLabel::ContactInfo(cluster_info.id());
        assert!(cluster_info.gossip.crds.lookup(&entry_label).is_some());
```

## Snippet 3

Context: `core/src/cluster_info.rs:177` (changes a sensitive control or state-update path)

Before
```rust
keypair,
            gossip_leader_id: Pubkey::default(),
        };
        let id = node_info.id;
        me.gossip.set_self(id);
        me.insert_info(node_info);
        me.push_self(&HashMap::new());
        me
```
After
```rust
keypair,
            gossip_leader_id: Pubkey::default(),
            entrypoint: None,
        };
        let id = node_info.id;
        me.gossip.set_self(id);
        me.insert_self(node_info);
        me.push_self(&HashMap::new());
```

## Snippet 4

Context: `core/src/cluster_info.rs:819` (changes a sensitive control or state-update path)

Before
```rust
})
            .collect();
        pr.into_iter()
            .map(|(peer, filter, gossip, self_info)| {
```
After
```rust
})
            .collect();
        if pr.is_empty() {
            self.add_entrypoint(&mut pr);
        } else {
            self.entrypoint = None;
        }
        pr.into_iter()
```

# Fix Pattern

Use a self-specific insertion path for identity-bearing gossip records. Enforce the local identity match before signing, sign with the local keypair, and reject mismatched self records instead of passing them through generic CRDS insertion.

## How It Was Fixed

The patch adds insert_self and uses it during ClusterInfo initialization. insert_self checks self.id() == node_info.id, signs the ContactInfo with self.keypair, and inserts the signed value into CRDS only on a match. It adds regression coverage for accepting the local self record and rejecting a different NodeInfo. It also adds an entrypoint fallback in gossip pull setup for bootstrapping when no peers are available.

# Why It Matters

1. CRDS ContactInfo is identity-bearing gossip control-plane data.

2. Self records should not be signed or propagated for a different advertised Pubkey.

3. The patch strengthens the identity-binding boundary for locally injected gossip records.

4. The evidence supports incorrectly signed gossip propagation, not transaction parsing, panics, ledger corruption, or proven remote exploitation.

# Evidence Notes

Grounded evidence comes from core/src/cluster_info.rs: ClusterInfo::new now calls insert_self; insert_self checks the id, signs ContactInfo with self.keypair, and inserts into CRDS; test_insert_self verifies the self record exists and a mismatched identity is not inserted; new_pull_requests uses add_entrypoint only when normal pull targets are unavailable. The commit subject explicitly references incorrectly signed gossip messages. The evidence does not show the full insert_info implementation, exact pre-patch signing behavior, remote attacker control, consensus impact, or behavior in the other modified files. Protocol security invariant: A node's self ContactInfo in CRDS gossip should be bound to the node identity it advertises: self-record insertion should only accept node_info.id equal to the local ClusterInfo id, and the resulting ContactInfo should be signed with the local keypair before propagation. Verification notes: The patch evidence does not prove remote exploitability by itself. The evidence does not show a consensus safety failure or ledger state corruption. The evidence does not support the heuristic claim about malformed transactions or panic-prone conversion. The entrypoint fallback may affect discovery/liveness, but the shown security invariant is about signed gossip identity binding. The exact behavior of modified files outside the provided hunks is not established from this input. Do not retain the heuristic transaction parsing or panic claims; they are unsupported by the provided evidence. Remote exploitability is not established from the shown hunks. Consensus, ledger, and storage-security impact are not established. The entrypoint changes look partly liveness-related, but the security-relevant part is the self ContactInfo identity/signature binding. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gossip-signature-integrity`
Final impact type: `integrity`
Final tags: `blockchain-core, p2p-networking, gossip, signature, identity-binding, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven concrete security fix. The change introduces a self-specific ContactInfo insertion path that checks the advertised node id against the local ClusterInfo id, signs the value with the local keypair, and rejects mismatched self records. That clearly tightens a security-sensitive gossip identity/signature boundary, especially with the commit subject referencing incorrectly signed gossip messages, but the evidence does not prove remote exploitability, consensus impact, or a liveness failure.

## Security Evidence

1. ClusterInfo::new now calls insert_self instead of generic insert_info for the local node record.
2. insert_self only inserts when self.id() == node_info.id.
3. insert_self signs CrdsValue::ContactInfo with the local keypair before CRDS insertion.
4. The new test verifies that a mismatched NodeInfo is not inserted through the self path.
5. The commit subject explicitly references fixing propagation of incorrectly signed gossip messages.

## Missing Evidence

1. No full pre-patch insert_info behavior is shown.
2. No evidence shows a remote attacker could trigger or exploit the bad signing path.
3. No evidence proves consensus safety impact, ledger corruption, or storage impact.
4. No evidence proves a concrete network-wide liveness failure from the bug.

## Claim Boundaries

1. Validate as security-hardening around gossip identity/signature binding.
2. Do not claim proven remote exploitability from the supplied evidence.
3. Do not classify primarily as liveness-failure based on the shown patch.
4. Do not claim transaction, RPC, ledger, or consensus impacts beyond the gossip control-plane evidence.
